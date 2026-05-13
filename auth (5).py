from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import (
    create_comment,
    get_all_comments,
    get_comment_by_id,
    get_comments_by_post,
    update_comment,
    delete_comment,
)


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_new_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_comment(db, comment_data, current_user.id)


@router.get("/", response_model=List[CommentResponse])
def read_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_all_comments(db, skip, limit)


@router.get("/post/{post_id}", response_model=List[CommentResponse])
def read_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_comments_by_post(db, post_id, skip, limit)


@router.get("/{comment_id}", response_model=CommentResponse)
def read_single_comment(comment_id: int, db: Session = Depends(get_db)):
    return get_comment_by_id(db, comment_id)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_existing_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_comment(db, comment_id, comment_data, current_user)


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return delete_comment(db, comment_id, current_user)
