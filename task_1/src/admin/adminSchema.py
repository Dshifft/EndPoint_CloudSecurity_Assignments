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
