from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import SecretStr

from config import Settings
from utils.data_types import UserJWTPayload


settings = Settings()
oauth2_schema = HTTPBearer()


def hash_context() -> CryptContext:
    """Use the same password-hash schemes as the reference project."""
    return CryptContext(schemes=["bcrypt", "sha256_crypt", "argon2"], deprecated="auto")


def hash_password(password: SecretStr) -> str:
    """Hash a password before it is stored in the temporary database."""
    return hash_context().hash(password.get_secret_value())


def verify_password(password: SecretStr, hashed_password: str) -> bool:
    """Compare a password with the hash stored for a user."""
    return hash_context().verify(password.get_secret_value(), hashed_password)


def generate_user_jwt(payload: UserJWTPayload) -> str:
    """Create a signed JWT after successful user authentication."""
    return jwt.encode(
        payload.model_dump(),
        settings.USER_JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def validate_user_jwt_token(
    header: HTTPAuthorizationCredentials = Depends(oauth2_schema),
) -> UserJWTPayload:
    """Decode and validate the bearer token used by protected user routes."""
    try:
        payload_data = jwt.decode(
            header.credentials,
            settings.USER_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return UserJWTPayload(**payload_data)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token.")
