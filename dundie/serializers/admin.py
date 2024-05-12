from datetime import datetime
from pydantic import BaseModel
from dundie.security import get_password_hash


class UserAdminResponse(BaseModel):
    """User response serializer containing basic information about a user."""

    id: int
    created_at: datetime
    is_active: bool
    private: bool
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


class FullUserDataResponse(BaseModel):
    """User response serializer containing full information about a user."""

    id: int
    created_at: datetime
    name: str
    username: str
    email: str
    dept: str
    avatar: str | None
    bio: str | None
    github: str | None
    linkedin: str | None
    instagram: str | None
    is_active: bool
    private: bool
    currency: str
    last_password_change: datetime


class FullUserPatchRequest(BaseModel):
    """User request serializer for creating or updating a user."""

    email: str
    new_password: str
    admin_password: str
    name: str
    dept: str
    username: str
    is_active: bool
    private: bool

    @property
    def hashed_password(self) -> str:
        """Returns hashed password"""
        return get_password_hash(self.new_password)
