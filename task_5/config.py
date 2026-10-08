from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


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

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    def get_postgres_url(self, host: str | None = None, port: int | None = None) -> URL:
        """Build the PostgreSQL SQLAlchemy connection URL."""
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=host if host is not None else self.POSTGRES_HOST,
            port=port if port is not None else self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

    model_config = SettingsConfigDict(env_file=".env")
