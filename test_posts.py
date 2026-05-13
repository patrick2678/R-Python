from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session):
    return db.query(User).all()


def update_user_role(db: Session, user_id: int, new_role: str):
    allowed_roles = ["admin", "author", "reader"]

    if new_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = new_role
    db.commit()
    db.refresh(user)

    logger.info(f"User role updated: user_id={user.id}, role={new_role}")

    return user

def update_current_user(db: Session, current_user: User, user_data):
    if user_data.username is not None:
        existing_username = get_user_by_username(db, user_data.username)
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_data.username

    if user_data.email is not None:
        existing_email = get_user_by_email(db, user_data.email)
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)

    logger.info(f"User profile updated: user_id={current_user.id}")

    return current_user
