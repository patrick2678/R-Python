from sqlalchemy.orm import Session

from app.config import ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
from app.core.security import hash_password
from app.models.user import User


def create_admin_if_not_exists(db: Session):
    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if existing_admin:
        return existing_admin

    admin_user = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        hashed_password=hash_password(ADMIN_PASSWORD),
        role="admin"
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return admin_user