from pydantic import BaseModel, root_validator

from dundie.models.user import get_username
from fastapi import HTTPException


class UserResponse(BaseModel):
    """User response serializer containing basic information about a user."""

    name: str
    username: str
    dept: str
    currency: str
    bio: str | None = None
    avatar: str | None = None


class UserRequest(BaseModel):
    """User request serializer for creating or updating a user."""

    email: str
    password: str
    name: str
    dept: str
    username: str | None = None
    avatar: str | None = None
    bio: str | None = None
    currency: str = "USD"

    @root_validator(pre=True)
    def get_username_if_not_exist(cls, values: dict) -> dict:
        """
        A root validator that gets the username if it does not exist in the
        user request.

        Args:
            cls: The class object.
            values: The dictionary of values.

        Returns:
            The updated dictionary of values.
        """

        if values.get('username') is None:
            values['username'] = get_username(values['name'])

        return values


class UserPatchRequest(BaseModel):
    """User request serializer for creating or updating a user."""

    email: str | None = None
    password: str | None = None
    name: str | None = None
    dept: str | None = None
    username: str | None = None
    avatar: str | None = None
    bio: str | None = None
    currency: str | None = None

    @root_validator(pre=True)
    def ensure_values(cls, values):
        if not values:
            raise HTTPException(400, 'Bad request, no data informed.')
        return values
