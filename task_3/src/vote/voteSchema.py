from pydantic import BaseModel


class VoteResponse(BaseModel):
    """Public information stored for a vote."""

    vote_id: int
    user_id: int
    candidate_id: int
