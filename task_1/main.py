from fastapi import FastAPI

from src.user.userEndpoints import user_router
from utils.constants import Endpoints

voting_app = FastAPI(
    title="Voting App",
    description="Initial API structure for the voting system.",
    version="0.1.0",
)

# The user router is introduced in Phase 1.
voting_app.include_router(user_router)


@voting_app.get(Endpoints.ROOT)
def read_root() -> dict[str, str]:
    """Simple route used to confirm that the API is running."""
    return {"message": "Welcome to the voting app!"}
