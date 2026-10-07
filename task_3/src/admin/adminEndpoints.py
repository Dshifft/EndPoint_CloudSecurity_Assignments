import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from config import Settings
from src.admin.adminSchema import (
    AdminLoginData,
    AdminLoginResponse,
    AdminMFARequestData,
    AdminMFAResponse,
    AdminRegData,
    AdminRegResponse,
    AdminValidateResponse,
    CandidateRegData,
    CandidateRegResponse,
    CandidateResponse,
)
from utils.constants import Endpoints
from utils.data_types import AdminJWTPayload
from utils.db import get_db
from utils.db_model import Admin, Candidate
from utils.email_service import send_mfa_email
from utils.logger import get_logger
from utils.security import generate_admin_jwt, hash_password, validate_admin_jwt_token, verify_password


settings = Settings()
logger = get_logger(__name__)
admin_router = APIRouter(prefix=Endpoints.ADMIN, tags=["admin"])


@admin_router.post(Endpoints.REGISTER, status_code=status.HTTP_201_CREATED, response_model=AdminRegResponse)
def register_admin(admin_reg_data: AdminRegData, db: Session = Depends(get_db)) -> AdminRegResponse:
    """Register an administrator and store only a hash of the password."""
    existing_admin = db.query(Admin).filter(Admin.email == str(admin_reg_data.email)).first()
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin with this email already exists.")

    admin = Admin(
        name=admin_reg_data.name,
        email=str(admin_reg_data.email),
        hashed_password=hash_password(admin_reg_data.password),
    )
    db.add(admin)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin with this email already exists.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to register administrator.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("Administrator registered.")
    return AdminRegResponse(name=admin_reg_data.name, email=admin_reg_data.email)


@admin_router.post(Endpoints.REQUEST_MFA, response_model=AdminMFAResponse)
def request_mfa_code(mfa_request: AdminMFARequestData, db: Session = Depends(get_db)) -> AdminMFAResponse:
    """Verify administrator credentials and send a one-time MFA code."""
    admin = db.query(Admin).filter(Admin.email == str(mfa_request.email)).first()
    if not admin or not verify_password(mfa_request.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    mfa_code = f"{secrets.randbelow(1_000_000):06d}"
    admin.mfa_code_hash = hash_password(SecretStr(mfa_code))
    admin.mfa_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.MFA_CODE_EXPIRE_MINUTES)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to save administrator MFA code.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

    try:
        send_mfa_email(admin.email, mfa_code)
    except Exception:
        logger.error("Unable to send MFA email.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to send MFA email.")

    logger.info("Administrator MFA code requested.")
    return AdminMFAResponse()


@admin_router.post(Endpoints.LOGIN, response_model=AdminLoginResponse)
def login_admin(admin_login_data: AdminLoginData, db: Session = Depends(get_db)) -> AdminLoginResponse:
    """Verify administrator password and MFA code before issuing a token."""
    admin = db.query(Admin).filter(Admin.email == str(admin_login_data.email)).first()
    if not admin or not verify_password(admin_login_data.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not admin.mfa_code_hash or not admin.mfa_code_expires_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA code is missing or expired.")
    if admin.mfa_code_expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA code is missing or expired.")
    if not verify_password(admin_login_data.mfa_code, admin.mfa_code_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code.")

    admin.mfa_code_hash = None
    admin.mfa_code_expires_at = None
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to consume administrator MFA code.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("Administrator logged in with MFA.")
    return AdminLoginResponse(token=generate_admin_jwt(AdminJWTPayload(email=admin.email)))


@admin_router.get(Endpoints.ROOT, response_model=AdminValidateResponse)
@admin_router.get(Endpoints.VALIDATE, response_model=AdminValidateResponse, include_in_schema=False)
def get_admin(
    admin_payload: AdminJWTPayload = Depends(validate_admin_jwt_token),
    db: Session = Depends(get_db),
) -> AdminValidateResponse:
    """Return the authenticated administrator."""
    admin = db.query(Admin).filter(Admin.email == admin_payload.email).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    logger.info("Administrator token validated.")
    return AdminValidateResponse(admin_payload=admin_payload)


@admin_router.delete(Endpoints.ROOT, status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_payload: AdminJWTPayload = Depends(validate_admin_jwt_token),
    db: Session = Depends(get_db),
) -> None:
    """Delete the authenticated administrator from PostgreSQL."""
    admin = db.query(Admin).filter(Admin.email == admin_payload.email).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    db.delete(admin)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to delete administrator.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("Administrator account deleted.")


@admin_router.post(Endpoints.CANDIDATE, status_code=status.HTTP_201_CREATED, response_model=CandidateRegResponse)
def register_candidate(
    candidate_reg_data: CandidateRegData,
    admin_payload: AdminJWTPayload = Depends(validate_admin_jwt_token),
    db: Session = Depends(get_db),
) -> CandidateRegResponse:
    """Register a candidate for the authenticated administrator."""
    admin = db.query(Admin).filter(Admin.email == admin_payload.email).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")

    candidate = Candidate(
        name=candidate_reg_data.name,
        email=str(candidate_reg_data.email),
        admin_id=admin.admin_id,
    )
    db.add(candidate)
    try:
        db.commit()
        db.refresh(candidate)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to register candidate.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("Candidate registered.")
    return CandidateRegResponse(
        candidate_id=candidate.candidate_id,
        name=candidate.name,
        email=candidate.email,
    )


@admin_router.get(Endpoints.CANDIDATE, response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db)) -> list[CandidateResponse]:
    """Return the public list of registered candidates."""
    candidates = db.query(Candidate).all()
    return [
        CandidateResponse(
            candidate_id=candidate.candidate_id,
            name=candidate.name,
            email=candidate.email,
            admin_id=candidate.admin_id,
        )
        for candidate in candidates
    ]
