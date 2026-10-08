from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.user.userSchema import (
    UserLoginData,
    UserLoginResponse,
    UserRegData,
    UserRegResponse,
    UserValidateResponse,
    VoteData,
    VoteRegResponse,
)
from utils.constants import Endpoints
from utils.data_types import UserJWTPayload
from utils.db import get_db
from utils.db_model import Candidate, User, Vote
from utils.logger import get_logger
from utils.security import generate_user_jwt, hash_password, validate_user_jwt_token, verify_password


logger = get_logger(__name__)
user_router = APIRouter(prefix=Endpoints.USER, tags=["user"])


@user_router.post(Endpoints.REGISTER, status_code=status.HTTP_201_CREATED, response_model=UserRegResponse)
def register_user(user_reg_data: UserRegData, db: Session = Depends(get_db)) -> UserRegResponse:
    """Register a user and store only a hash of the supplied password."""
    existing_user = db.query(User).filter(User.email == str(user_reg_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")

    user = User(
        name=user_reg_data.name,
        email=str(user_reg_data.email),
        hashed_password=hash_password(user_reg_data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to register user.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("User registered.")
    return UserRegResponse(name=user_reg_data.name, email=user_reg_data.email)


@user_router.post(Endpoints.LOGIN, response_model=UserLoginResponse)
def login_user(user_login_data: UserLoginData, db: Session = Depends(get_db)) -> UserLoginResponse:
    """Verify user credentials and return a signed access token."""
    user = db.query(User).filter(User.email == str(user_login_data.email)).first()
    if not user or not verify_password(user_login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    logger.info("User logged in.")
    return UserLoginResponse(token=generate_user_jwt(UserJWTPayload(email=user.email)))


@user_router.get(Endpoints.ROOT, response_model=UserValidateResponse)
@user_router.get(Endpoints.VALIDATE, response_model=UserValidateResponse, include_in_schema=False)
def get_user(
    user_payload: UserJWTPayload = Depends(validate_user_jwt_token),
    db: Session = Depends(get_db),
) -> UserValidateResponse:
    """Return the authenticated user."""
    user = db.query(User).filter(User.email == user_payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    logger.info("User token validated.")
    return UserValidateResponse(user_payload=user_payload)


@user_router.delete(Endpoints.ROOT, status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_payload: UserJWTPayload = Depends(validate_user_jwt_token),
    db: Session = Depends(get_db),
) -> None:
    """Delete the authenticated user from PostgreSQL."""
    user = db.query(User).filter(User.email == user_payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    db.delete(user)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to delete user.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("User account deleted.")


@user_router.post(Endpoints.VOTE, status_code=status.HTTP_201_CREATED, response_model=VoteRegResponse)
def register_vote(
    vote_data: VoteData,
    user_payload: UserJWTPayload = Depends(validate_user_jwt_token),
    db: Session = Depends(get_db),
) -> VoteRegResponse:
    """Register the authenticated user's vote for a candidate."""
    user = db.query(User).filter(User.email == user_payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    existing_vote = db.query(Vote).filter(Vote.user_id == user.user_id).first()
    if existing_vote:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has already voted.")

    candidate = db.query(Candidate).filter(Candidate.candidate_id == vote_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    vote = Vote(user_id=user.user_id, candidate_id=candidate.candidate_id)
    db.add(vote)
    try:
        db.commit()
        db.refresh(vote)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has already voted.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Unable to register vote.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")
    logger.info("User vote registered.")
    return VoteRegResponse(vote_id=vote.vote_id, user_id=vote.user_id, candidate_id=vote.candidate_id)
