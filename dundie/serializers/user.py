from email_validator import (
    EmailNotValidError,
    EmailSyntaxError,
    EmailUndeliverableError,
    validate_email,
)
from fastapi import HTTPException
from pydantic import BaseModel, root_validator

from dundie.security import get_password_hash
from dundie.utils.utils import get_username, validate_user_fields


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
    currency: str = 'USD'

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

    @root_validator(pre=True)
    def check_email_syntax(cls, values: dict) -> dict:
        """
        Validates the syntax of an email address.

        This function is a root validator that is called before any other
        validators. It checks the syntax of the email address provided in the
        `values` dictionary. If the email address is not valid, it raises
        an HTTPException with a status code of 400 and the corresponding
        error message.

        Raises:
            HTTPException: If the email address is not valid.
        """
        email = values.get('email')
        try:
            validate_email(email)
        except (
            EmailSyntaxError,
            EmailNotValidError,
            EmailUndeliverableError,
        ) as e:
            raise HTTPException(400, str(e))

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
    def hashed_password(self) -> str:
        """Returns hashed password"""
        return get_password_hash(self.password)


class EmailRequest(BaseModel):
    email: str

    @root_validator(pre=True)
    def check_email_syntax(cls, values: dict) -> dict:
        """
        Validates the syntax of an email address.

        This function is a root validator that is called before any other
        validators. It checks the syntax of the email address provided in the
        `values` dictionary. If the email address is not valid, it raises
        an HTTPException with a status code of 400 and the corresponding
        error message.

        Raises:
            HTTPException: If the email address is not valid.
        """
        email = values.get('email')
        try:
            validate_email(email)

        except (
            EmailSyntaxError,
            EmailNotValidError,
            EmailUndeliverableError,
        ) as e:
            raise HTTPException(400, str(e))

        return values


class UserProfilePatchRequest(BaseModel):
    name: str
    username: str
    bio: str

    @root_validator(pre=True)
    def validate_values(values):
        try:
            validate_user_fields(values)
            return values

        except HTTPException as e:
            raise e

        except Exception:
            raise HTTPException(
                400, 'An error occurred while validating the data'
            )
