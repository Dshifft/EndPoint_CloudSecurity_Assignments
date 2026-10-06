import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import SecretStr

from config import Settings
from src.admin.adminSchema import (
    AdminLoginData,
    AdminLoginResponse,
    AdminMFARequestData,
    AdminMFAResponse,
    AdminRegData,
    AdminRegResponse,
    AdminValidateResponse,
)
from utils.constants import Endpoints
from utils.data_types import AdminJWTPayload
from utils.db import FakeDB, get_db
from utils.email_service import send_mfa_email
from utils.security import generate_admin_jwt, hash_password, validate_admin_jwt_token, verify_password


settings = Settings()
admin_router = APIRouter(prefix=Endpoints.ADMIN, tags=["admin"])


@admin_router.post(
    Endpoints.REGISTER,
    status_code=status.HTTP_201_CREATED,
    response_model=AdminRegResponse,
)
def register_admin(admin_reg_data: AdminRegData, db: FakeDB = Depends(get_db)) -> AdminRegResponse:
    """Register an administrator and store only a hash of the password."""
    if db.get_admin(str(admin_reg_data.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin with this email already exists.")

    admin_data = admin_reg_data.model_dump(exclude={"password"})
    admin_data["email"] = str(admin_reg_data.email)
    admin_data["hashed_password"] = hash_password(admin_reg_data.password)
    db.add_admin(admin_data)

    return AdminRegResponse(name=admin_reg_data.name, email=admin_reg_data.email)


@admin_router.post(Endpoints.REQUEST_MFA, response_model=AdminMFAResponse)
def request_mfa_code(mfa_request: AdminMFARequestData, db: FakeDB = Depends(get_db)) -> AdminMFAResponse:
    """Verify admin credentials and send a one-time MFA code by email."""
    admin = db.get_admin(str(mfa_request.email))
    if not admin or not verify_password(mfa_request.password, admin["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    mfa_code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.MFA_CODE_EXPIRE_MINUTES)
    db.save_admin_mfa(
        admin["email"],
        hash_password(SecretStr(mfa_code)),
        expires_at,
    )

    try:
        send_mfa_email(admin["email"], mfa_code)
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to send MFA email.")

    return AdminMFAResponse()


@admin_router.post(Endpoints.LOGIN, response_model=AdminLoginResponse)
def login_admin(admin_login_data: AdminLoginData, db: FakeDB = Depends(get_db)) -> AdminLoginResponse:
    """Verify admin password and MFA code before issuing an access token."""
    admin = db.get_admin(str(admin_login_data.email))
    if not admin or not verify_password(admin_login_data.password, admin["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    code_hash = admin.get("mfa_code_hash")
    expires_at = admin.get("mfa_code_expires_at")
    if not code_hash or not expires_at or expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA code is missing or expired.")
    if not verify_password(admin_login_data.mfa_code, code_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code.")

    db.clear_admin_mfa(admin["email"])
    token = generate_admin_jwt(AdminJWTPayload(email=admin["email"]))
    return AdminLoginResponse(token=token)


@admin_router.get(Endpoints.VALIDATE, response_model=AdminValidateResponse)
def validate_admin(
    admin_payload: AdminJWTPayload = Depends(validate_admin_jwt_token),
    db: FakeDB = Depends(get_db),
) -> AdminValidateResponse:
    """Validate the token and confirm that its admin still exists."""
    if not db.get_admin(admin_payload.email):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    return AdminValidateResponse(admin_payload=admin_payload)


@admin_router.delete(Endpoints.ROOT, status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_payload: AdminJWTPayload = Depends(validate_admin_jwt_token),
    db: FakeDB = Depends(get_db),
) -> None:
    """Delete the authenticated administrator from the temporary database."""
    if not db.get_admin(admin_payload.email):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found.")
    db.remove_admin(admin_payload.email)
