from pydantic import BaseModel, EmailStr, SecretStr


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
