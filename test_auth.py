from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import get_user_by_email, get_user_by_username
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, user_data: UserCreate):
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        logger.warning(f"Register failed: email already exists -> {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = get_user_by_username(db, user_data.username)
    if existing_username:
        logger.warning(f"Register failed: username already taken -> {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="reader"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email} with role {new_user.role}")

    return new_user


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Login failed: email not found -> {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(password, user.hashed_password):
        logger.warning(f"Login failed: wrong password -> {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": str(user.id)})

    logger.info(f"Login success: {email}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }