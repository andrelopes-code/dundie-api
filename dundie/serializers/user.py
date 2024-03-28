from pydantic import BaseModel, root_validator

from dundie.models.user import get_username


class UserResponse(BaseModel):
    """
    User response serializer containing basic information about a user.

    Attributes:
        username (str): Username
        avatar (str | None): User's avatar URL
        bio (str | None): User's bio
        name (str): User's full name
        dept (str): User's department
        currency (str): User's preferred currency
    """

    username: str
    avatar: str | None = None
    bio: str | None = None
    name: str
    dept: str
    currency: str


class UserRequest(BaseModel):
    """
    User request serializer for creating or updating a user.

    Attributes:
        email (str): User's email
        password (str): User's password
        name (str): User's full name
        dept (str): User's department
        username (str | None): Username
        avatar (str | None): User's avatar URL
        bio (str | None): User's bio
        currency (str): User's preferred currency
    """

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
