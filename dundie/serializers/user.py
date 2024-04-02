from fastapi import HTTPException
from pydantic import BaseModel, root_validator

from dundie.security import get_password_hash
from dundie.models.user import get_username


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

    avatar: str | None = None
    bio: str | None = None

    @root_validator(pre=True)
    def ensure_values(cls, values):
        if not values:
            raise HTTPException(400, 'Bad request, no data informed.')
        return values


class UserPasswordPatchRequest(BaseModel):
    password: str
    password_confirm: str

    @root_validator(pre=True)
    def check_passwords_match(cls, values):
        """Checks if passwords match"""
        if values.get('password') != values.get('password_confirm'):
            raise HTTPException(400, 'Passwords do not match')
        return values

    @property
    def hashed_password(self):
        """Returns hashed password"""
        get_password_hash(self.password)
