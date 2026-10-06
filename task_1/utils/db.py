class FakeDB:
    """Temporary in-memory storage used before PostgreSQL is introduced."""

    def __init__(self):
        self.admins = {}
        self.users = {}

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
