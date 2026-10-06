class FakeDB:
    """Temporary in-memory storage used before PostgreSQL is introduced."""

    def __init__(self):
        self.admins = {}
        self.users = {}

    def add_admin(self, admin_data: dict) -> None:
        self.admins[admin_data["email"]] = admin_data

    def get_admin(self, email: str) -> dict | None:
        return self.admins.get(email)

    def save_admin_mfa(self, email: str, code_hash: str, expires_at) -> None:
        """Store the hash and expiration of a temporary admin MFA code."""
        self.admins[email]["mfa_code_hash"] = code_hash
        self.admins[email]["mfa_code_expires_at"] = expires_at

    def clear_admin_mfa(self, email: str) -> None:
        """Remove an MFA code after it has been used successfully."""
        self.admins[email].pop("mfa_code_hash", None)
        self.admins[email].pop("mfa_code_expires_at", None)

    def add_user(self, user_data: dict) -> None:
        self.users[user_data["email"]] = user_data

    def get_user(self, email: str) -> dict | None:
        return self.users.get(email)

    def remove_user(self, email: str) -> None:
        if email not in self.users:
            raise ValueError("User not found.")
        del self.users[email]


# Data remains available while the API process is running.
db = FakeDB()


def get_db() -> FakeDB:
    """Provide the shared temporary database to FastAPI endpoints."""
    return db
