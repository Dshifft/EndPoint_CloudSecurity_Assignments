from fastapi import FastAPI

from utils.constants import Endpoints

voting_app = FastAPI(
    title="Voting App",
    description="Initial API structure for the voting system.",
    version="0.1.0",
)


@voting_app.get(Endpoints.ROOT)
def read_root() -> dict[str, str]:
    """Simple route used to confirm that the API is running."""
    return {"message": "Welcome to the voting app!"}
