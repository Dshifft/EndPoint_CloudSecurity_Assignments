from fastapi import FastAPI

from utils.logger import get_logger
from src.admin.adminEndpoints import admin_router
from src.user.userEndpoints import user_router
from utils.constants import Endpoints


logger = get_logger(__name__)
voting_app = FastAPI(
    title="Voting App",
    description="Initial API structure for the voting system.",
    version="0.1.0",
)

voting_app.include_router(user_router)
voting_app.include_router(admin_router)


@voting_app.on_event("startup")
def log_application_startup() -> None:
    """Record that the API is ready to receive requests."""
    logger.info("Voting API started.")


@voting_app.get(Endpoints.ROOT)
def read_root() -> dict[str, str]:
    """Simple route used to confirm that the API is running."""
    logger.info("Root endpoint requested.")
    return {"message": "Welcome to the voting app!"}
