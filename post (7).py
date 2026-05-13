from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services.posts_service import (
    create_post,
    get_all_posts,
    get_post_by_id,
    update_post,
    delete_post
)


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_new_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "reader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Readers are not allowed to create posts"
        )

    return create_post(db, post_data, current_user.id)

@router.get("/", response_model=List[PostResponse])
def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_all_posts(db, skip, limit)


@router.get("/{post_id}", response_model=PostResponse)
def read_single_post(post_id: int, db: Session = Depends(get_db)):
    return get_post_by_id(db, post_id)


@router.put("/{post_id}", response_model=PostResponse)
def update_existing_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_post(db, post_id, post_data, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_post(db, post_id, current_user)

