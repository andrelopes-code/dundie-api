import re
import time
import unicodedata
from datetime import datetime, timezone
from functools import wraps
from typing import TYPE_CHECKING

from fastapi import HTTPException
from dundie.db import engine
from dundie.config import settings
from sqlmodel import Session, select

if TYPE_CHECKING:
    from dundie.models import User
    from dundie.serializers import UserPatchRequest, UserProfilePatchRequest


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


def apply_user_profile_patch(
    user: 'User', patch_data: 'UserProfilePatchRequest'
) -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data (UserProfilePatchRequest): The patch data containing
        attributes and their new values.
    """
    from rich import print as bp
    bp("PATCH DATA: ", patch_data)
    bp("USER: ", user)
    for atribute, value in patch_data:
        if value is not None and value != '':
            bp(f"ATRIBUTO: {atribute}, VALOR: {value}")
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
    name = name.lower().replace(' ', '')

    chars = []

    for c in unicodedata.normalize('NFD', name):
        if unicodedata.category(c) != 'Mn':
            chars.append(c)

    return ''.join(chars)


def timer(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = await func(*args, **kwargs)
        fim = time.time()
        print(f"\033[36mTempo de execução: {fim - inicio}\033[m")
        return resultado

    return wrapper


def validate_name(name):
    name_pattern = re.compile(r'[a-z-A-ZÀ-ú\s]{8,50}$')
    if not name_pattern.match(name):
        raise HTTPException(status_code=400, detail="Name is not valid")
    return


def validate_username(username):
    with Session(engine) as session:
        from dundie.models import User
        stmt = select(User).where(User.username == username)
        if (
            session.exec(stmt).first()
            or username in settings.PRIVATE_USERNAMES
        ):
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
                )

    username_pattern = re.compile(r'[a-z]{3,50}$')
    if not username_pattern.match(username):
        raise HTTPException(status_code=400, detail="Username is not valid")
    return


def validate_bio(bio):
    if len(bio) > 255:
        raise HTTPException(status_code=400, detail="Bio is too long")
    return


def validate_user_fields(user: dict):
    # if data is "" bypass the validation
    if (name := user.get('name')) != "":
        validate_name(name)
    if (username := user.get('username')) != "":
        validate_username(username)
    if (bio := user.get('bio')) != "":
        validate_bio(bio)
