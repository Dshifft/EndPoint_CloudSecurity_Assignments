from pydantic import BaseModel, EmailStr, SecretStr


class UserRegData(BaseModel):
    """Data received when a voting user registers."""

    name: str
    email: EmailStr
    password: SecretStr


class UserRegResponse(BaseModel):
    message: str = "User registered successfully."
    name: str
    email: EmailStr


class UserLoginData(BaseModel):
    """Credentials received when a voting user logs in."""

    email: EmailStr
    password: SecretStr


class UserLoginResponse(BaseModel):
    message: str = "User logged in successfully."
    token: str
