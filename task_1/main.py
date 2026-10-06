from fastapi import FastAPI

from src.admin.adminEndpoints import admin_router
from src.user.userEndpoints import user_router
from utils.constants import Endpoints

voting_app = FastAPI(
    title="Voting App",
    description="Initial API structure for the voting system.",
    version="0.1.0",
)

# User and administrator routers are added as their phases are completed.
voting_app.include_router(user_router)
voting_app.include_router(admin_router)


@voting_app.get(Endpoints.ROOT)
def read_root() -> dict[str, str]:
    """Simple route used to confirm that the API is running."""
    return {"message": "Welcome to the voting app!"}
