from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read JWT settings from the local .env file."""

    USER_JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    USER_JWT_EXPIRE_DAYS: int = 1
    ADMIN_JWT_SECRET: str
    ADMIN_JWT_EXPIRE_DAYS: int = 1
    MFA_CODE_EXPIRE_MINUTES: int = 10

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: SecretStr
    SMTP_FROM: str

    model_config = SettingsConfigDict(env_file=".env")
