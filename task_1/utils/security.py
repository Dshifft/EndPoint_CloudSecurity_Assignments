from passlib.context import CryptContext
from pydantic import SecretStr


def hash_context() -> CryptContext:
    """Use the same password-hash schemes as the reference project."""
    return CryptContext(schemes=["bcrypt", "sha256_crypt", "argon2"], deprecated="auto")


def hash_password(password: SecretStr) -> str:
    """Hash a password before it is stored in the temporary database."""
    return hash_context().hash(password.get_secret_value())
