from datetime import datetime

from pydantic import BaseModel


class UserAdminResponse(BaseModel):
    """User response serializer containing basic information about a user."""

    id: int
    created_at: datetime
    is_active: bool
    name: str
    username: str
    email: str
    dept: str
    avatar: str | None
    bio: str | None
    github: str | None
    linkedin: str | None
    instagram: str | None


class UserChangeVisibilityRequest(BaseModel):
    """User request serializer for deleting a user."""

    username: str
    password: str
    disable: bool
    enable: bool
