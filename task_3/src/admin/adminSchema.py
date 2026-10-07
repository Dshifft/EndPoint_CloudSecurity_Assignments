from pydantic import BaseModel, EmailStr, SecretStr

from utils.data_types import AdminJWTPayload


class AdminRegData(BaseModel):
    """Data received when an administrator registers."""

    name: str
    email: EmailStr
    password: SecretStr


class AdminRegResponse(BaseModel):
    message: str = "Admin registered successfully."
    name: str
    email: EmailStr


class AdminMFARequestData(BaseModel):
    """Credentials required before an administrator receives an MFA code."""

    email: EmailStr
    password: SecretStr


class AdminMFAResponse(BaseModel):
    message: str = "MFA code sent to the administrator email."


class AdminLoginData(BaseModel):
    """Credentials and MFA code required for administrator login."""

    email: EmailStr
    password: SecretStr
    mfa_code: SecretStr


class AdminLoginResponse(BaseModel):
    message: str = "Admin logged in successfully."
    token: str


class AdminValidateResponse(BaseModel):
    message: str = "Admin token is valid."
    admin_payload: AdminJWTPayload


class CandidateRegData(BaseModel):
    """Data received when an administrator registers a candidate."""

    name: str
    email: EmailStr


class CandidateRegResponse(BaseModel):
    message: str = "Candidate registered successfully."
    candidate_id: int
    name: str
    email: EmailStr


class CandidateResponse(BaseModel):
    """Public information stored for a candidate."""

    candidate_id: int
    name: str
    email: EmailStr
    admin_id: int | None
