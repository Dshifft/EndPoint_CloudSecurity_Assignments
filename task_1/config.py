from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read JWT settings from the local .env file."""

    USER_JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    USER_JWT_EXPIRE_DAYS: int = 1

    model_config = SettingsConfigDict(env_file=".env")
