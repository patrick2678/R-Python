from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    post_id: int
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    user_id: int
    post_id: int
    parent_id: int | None
    created_at: datetime
