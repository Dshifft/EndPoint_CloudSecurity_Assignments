from fastapi import APIRouter, Depends, HTTPException, status

from src.user.userSchema import UserRegData, UserRegResponse
from utils.constants import Endpoints
from utils.db import FakeDB, get_db
from utils.security import hash_password


user_router = APIRouter(prefix=Endpoints.USER, tags=["user"])


@user_router.post(
    Endpoints.REGISTER,
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegResponse,
)
def register_user(user_reg_data: UserRegData, db: FakeDB = Depends(get_db)) -> UserRegResponse:
    """Register a user and store only a hash of the supplied password."""
    if db.get_user(str(user_reg_data.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")

    user_data = user_reg_data.model_dump(exclude={"password"})
    user_data["email"] = str(user_reg_data.email)
    user_data["hashed_password"] = hash_password(user_reg_data.password)
    db.add_user(user_data)

    return UserRegResponse(name=user_reg_data.name, email=user_reg_data.email)
