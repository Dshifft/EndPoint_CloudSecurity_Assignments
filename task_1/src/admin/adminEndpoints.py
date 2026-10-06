from fastapi import APIRouter, Depends, HTTPException, status

from src.admin.adminSchema import AdminRegData, AdminRegResponse
from utils.constants import Endpoints
from utils.db import FakeDB, get_db
from utils.security import hash_password


admin_router = APIRouter(prefix=Endpoints.ADMIN, tags=["admin"])


@admin_router.post(
    Endpoints.REGISTER,
    status_code=status.HTTP_201_CREATED,
    response_model=AdminRegResponse,
)
def register_admin(admin_reg_data: AdminRegData, db: FakeDB = Depends(get_db)) -> AdminRegResponse:
    """Register an administrator and store only a hash of the password."""
    if db.get_admin(str(admin_reg_data.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin with this email already exists.")

    admin_data = admin_reg_data.model_dump(exclude={"password"})
    admin_data["email"] = str(admin_reg_data.email)
    admin_data["hashed_password"] = hash_password(admin_reg_data.password)
    db.add_admin(admin_data)

    return AdminRegResponse(name=admin_reg_data.name, email=admin_reg_data.email)
