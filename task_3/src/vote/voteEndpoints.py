from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.vote.voteSchema import VoteResponse
from utils.constants import Endpoints
from utils.db import get_db
from utils.db_model import Vote


vote_router = APIRouter(tags=["vote"])


@vote_router.get(Endpoints.VOTES, response_model=list[VoteResponse])
def get_votes(db: Session = Depends(get_db)) -> list[VoteResponse]:
    """Return the public list of registered votes."""
    votes = db.query(Vote).all()
    return [
        VoteResponse(vote_id=vote.vote_id, user_id=vote.user_id, candidate_id=vote.candidate_id)
        for vote in votes
    ]
