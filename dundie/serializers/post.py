from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel, root_validator


class PostUserResponse(BaseModel):
    """User response serializer containing basic information about a user."""
    id: int
    name: str
    username: str
    dept: str
    avatar: str | None


class PostResponse(BaseModel):
    """User response serializer containing basic information about a user."""

    id: int
    date: datetime
    content: str
    user: PostUserResponse
    likes: int


class PostRequest(BaseModel):
    content: str

    @root_validator(pre=True)
    def check_content(cls, values):

        content = values.get('content')

        if content == '':
            raise HTTPException(400, 'Content cannot be empty')

        if len(content) > 1000:
            raise HTTPException(400, 'Content is too long')

        return values
