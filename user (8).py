from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.user import UserResponse, UserRoleUpdate, UserUpdate
from app.services.user_service import get_all_users, update_user_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserResponse])
def read_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return get_all_users(db)


@router.put("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_user_role(db, user_id, role_data.role)

@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.services.user_service import update_current_user
    return update_current_user(db, current_user, user_data)