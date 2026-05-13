from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.cache import get_cache, set_cache, delete_cache, delete_cache_pattern
from app.core.logger import logger
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


def create_post(db: Session, post_data: PostCreate, author_id: int):
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=author_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    delete_cache_pattern("posts:*")
    delete_cache(f"post:{new_post.id}")

    logger.info(f"Post created: id={new_post.id}, author_id={author_id}")

    return new_post


def get_all_posts(db: Session, skip: int = 0, limit: int = 10):
    cache_key = f"posts:{skip}:{limit}"
    cached_posts = get_cache(cache_key)

    if cached_posts:
        logger.info(f"Posts fetched from cache: skip={skip}, limit={limit}")
        return cached_posts

    logger.info(f"Fetching posts from database with skip={skip}, limit={limit}")
    posts = db.query(Post).offset(skip).limit(limit).all()

    posts_data = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
        }
        for post in posts
    ]

    set_cache(cache_key, posts_data)
    return posts_data


def get_post_by_id(db: Session, post_id: int):
    cache_key = f"post:{post_id}"
    cached_post = get_cache(cache_key)

    if cached_post:
        logger.info(f"Post fetched from cache: id={post_id}")
        return cached_post

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        logger.warning(f"Post not found: id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post_data = {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at,
    }

    set_cache(cache_key, post_data)
    return post_data


def update_post(db: Session, post_id: int, post_data: PostUpdate, current_user):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        logger.warning(f"Update failed: post not found id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != current_user.id and current_user.role != "admin":
        logger.warning(f"Unauthorized update attempt: user_id={current_user.id}, post_id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this post"
        )

    if post_data.title is not None:
        post.title = post_data.title

    if post_data.content is not None:
        post.content = post_data.content

    db.commit()
    db.refresh(post)

    delete_cache_pattern("posts:*")
    delete_cache(f"post:{post_id}")

    logger.info(f"Post updated: id={post.id}, by user_id={current_user.id}")

    return post


def delete_post(db: Session, post_id: int, current_user):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        logger.warning(f"Delete failed: post not found id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != current_user.id and current_user.role != "admin":
        logger.warning(f"Unauthorized delete attempt: user_id={current_user.id}, post_id={post_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this post"
        )

    comment_ids = [
        row[0]
        for row in db.query(Comment.id).filter(Comment.post_id == post_id).all()
    ]
    db.query(Comment).filter(Comment.post_id == post_id).delete(synchronize_session=False)
    db.delete(post)
    db.commit()

    delete_cache_pattern("posts:*")
    delete_cache_pattern("comments:*")
    delete_cache(f"post:{post_id}")
    for comment_id in comment_ids:
        delete_cache(f"comment:{comment_id}")

    logger.info(f"Post deleted: id={post_id}, by user_id={current_user.id}")

    return {"message": "Post deleted successfully"}
