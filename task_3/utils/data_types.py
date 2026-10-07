from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field

from config import Settings


settings = Settings()


class UserJWTPayload(BaseModel):
    """Data stored in a user access token."""

    email: str
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=settings.USER_JWT_EXPIRE_DAYS)
    )


class AdminJWTPayload(BaseModel):
    """Data stored in an administrator access token."""

    email: str
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=settings.ADMIN_JWT_EXPIRE_DAYS)
    )
