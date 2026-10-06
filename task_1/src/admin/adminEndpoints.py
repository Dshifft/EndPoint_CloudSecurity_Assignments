import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import SecretStr

from config import Settings
from src.admin.adminSchema import AdminMFARequestData, AdminMFAResponse, AdminRegData, AdminRegResponse
from utils.constants import Endpoints
from utils.db import FakeDB, get_db
from utils.email_service import send_mfa_email
from utils.security import hash_password, verify_password


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
