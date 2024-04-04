from datetime import datetime, timezone
from typing import TYPE_CHECKING
import unicodedata

if TYPE_CHECKING:
    from dundie.serializers import UserPatchRequest
    from dundie.models import User


def apply_user_patch(user: 'User', patch_data: 'UserPatchRequest') -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data (UserPatchRequest): The patch data containing
        attributes and their new values.
    """
    for atribute, value in patch_data:
        if value is not None:
            setattr(user, atribute, value)


def get_utcnow():
    """Gets the current utc datetime"""
    return datetime.now(timezone.utc)


def get_username(name: str) -> str:
    """
    Converts a given name into a username-friendly format by removing accents
    and spaces, and converting it to lowercase.

    Args:
        name (str): The input name to be converted into a username.

    Returns:
        str: The username-friendly version of the input name.
    """
    # Convert name to lowercase and replace spaces with hyphens
    name = name.lower().replace(' ', '-')

    chars = []

    for c in unicodedata.normalize('NFD', name):
        if unicodedata.category(c) != 'Mn':
            chars.append(c)

    return ''.join(chars)
