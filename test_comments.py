from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.cache import delete_cache, delete_cache_pattern, get_cache, set_cache
from app.core.logger import logger
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate, CommentUpdate


def _comment_to_dict(comment: Comment):
    return {
        "id": comment.id,
        "content": comment.content,
        "user_id": comment.user_id,
        "post_id": comment.post_id,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at,
    }


def _invalidate_comment_cache(comment_id: int | None = None):
    delete_cache_pattern("comments:*")
    if comment_id is not None:
        delete_cache(f"comment:{comment_id}")


def create_comment(db: Session, comment_data: CommentCreate, user_id: int):
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        logger.warning(f"Comment creation failed: post not found id={comment_data.post_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if comment_data.parent_id is not None:
        parent_comment = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent_comment:
            logger.warning(f"Reply failed: parent comment not found id={comment_data.parent_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )

        if parent_comment.post_id != comment_data.post_id:
            logger.warning("Reply failed: parent comment does not belong to the same post")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment does not belong to this post"
            )

    new_comment = Comment(
        content=comment_data.content,
        user_id=user_id,
        post_id=comment_data.post_id,
        parent_id=comment_data.parent_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    _invalidate_comment_cache(new_comment.id)

    logger.info(f"Comment created: id={new_comment.id}, user_id={user_id}, post_id={comment_data.post_id}")

    return new_comment


def get_all_comments(db: Session, skip: int = 0, limit: int = 10):
    cache_key = f"comments:all:{skip}:{limit}"
    cached_comments = get_cache(cache_key)

    if cached_comments:
        logger.info(f"Comments fetched from cache: skip={skip}, limit={limit}")
        return cached_comments

    logger.info(f"Fetching comments from database with skip={skip}, limit={limit}")
    comments = db.query(Comment).offset(skip).limit(limit).all()
    comments_data = [_comment_to_dict(comment) for comment in comments]
    set_cache(cache_key, comments_data)
    return comments_data


def get_comment_by_id(db: Session, comment_id: int):
    cache_key = f"comment:{comment_id}"
    cached_comment = get_cache(cache_key)

    if cached_comment:
        logger.info(f"Comment fetched from cache: id={comment_id}")
        return cached_comment

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        logger.warning(f"Comment fetch failed: comment not found id={comment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment_data = _comment_to_dict(comment)
    set_cache(cache_key, comment_data)
    return comment_data


def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 10):
    cache_key = f"comments:post:{post_id}:{skip}:{limit}"
    cached_comments = get_cache(cache_key)

    if cached_comments:
        logger.info(f"Post comments fetched from cache: post_id={post_id}, skip={skip}, limit={limit}")
        return cached_comments

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        logger.warning(f"Comments fetch failed: post not found id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    logger.info(f"Fetching comments for post_id={post_id}, skip={skip}, limit={limit}")

    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    comments_data = [_comment_to_dict(comment) for comment in comments]
    set_cache(cache_key, comments_data)
    return comments_data


def update_comment(db: Session, comment_id: int, comment_data: CommentUpdate, current_user):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        logger.warning(f"Comment update failed: comment not found id={comment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id and current_user.role != "admin":
        logger.warning(f"Unauthorized comment update: user_id={current_user.id}, comment_id={comment_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this comment"
        )

    if comment_data.content is not None:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)

    _invalidate_comment_cache(comment.id)

    logger.info(f"Comment updated: id={comment.id}, by user_id={current_user.id}")

    return comment


def delete_comment(db: Session, comment_id: int, current_user):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        logger.warning(f"Comment delete failed: comment not found id={comment_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment.user_id != current_user.id and current_user.role != "admin":
        logger.warning(f"Unauthorized comment delete: user_id={current_user.id}, comment_id={comment_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this comment"
        )

    db.delete(comment)
    db.commit()

    _invalidate_comment_cache(comment_id)

    logger.info(f"Comment deleted: id={comment_id}, by user_id={current_user.id}")

    return {"message": "Comment deleted successfully"}
