import re
import unicodedata
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request
from sqlmodel import Session, select
from dundie.security import verify_password
from dundie.config import settings
from dundie.db import engine

if TYPE_CHECKING:
    from dundie.models import User, Products


def apply_user_patch(user: 'User', patch_data: any, ignore: list = []) -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data: The patch data containing
        attributes and their new values.
    """
    for atribute, value in patch_data:
        if value is not None and atribute not in ignore:
            setattr(user, atribute, value)


def apply_product_patch(
    product: 'Products', patch_data: any, ignore: list = []
) -> None:
    """
    Updates the product object with the provided patch data.

    Args:
        product (Products): The product object to be updated.
        patch_data: The patch data containing
        attributes and their new values.
    """
    for atribute, value in patch_data:
        if value is not None and atribute not in ignore:
            setattr(product, atribute, value)


def apply_user_profile_patch(
    user: 'User', patch_data: any, ignore: list = []
) -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data: The patch data containing
        attributes and their new values.
    """
    for atribute, value in patch_data:
        if value is not None and value != '' and atribute not in ignore:
            setattr(user, atribute, value)


def apply_user_links_patch(user: 'User', patch_data: any) -> None:
    """
    Updates the user object with the provided patch data.

    Args:
        user (User): The user object to be updated.
        patch_data: The patch data containing
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
    name = name.lower().replace(' ', '')

    chars = []

    for c in unicodedata.normalize('NFD', name):
        if unicodedata.category(c) != 'Mn':
            chars.append(c)

    return ''.join(chars)


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
                status_code=409, detail="Username already exists"
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
    if name := user.get('name'):
        validate_name(name)
    if username := user.get('username'):
        validate_username(username)
    if bio := user.get('bio'):
        validate_bio(bio)


def validate_user_links(links: dict):

    github: str | None = links.get('github')
    linkedin: str | None = links.get('linkedin')
    instagram: str | None = links.get('instagram')

    if github:
        if not github.startswith(
            (
                'https://github.com/',
                'github.com/',
                'www.github.com/',
                'https://www.github.com',
            )
        ):
            raise HTTPException(400, 'Invalid github link')
    if linkedin:
        if not linkedin.startswith(
            (
                'https://linkedin.com/in/',
                'linkedin.com/in/',
                'www.linkedin.com/in/',
                'https://www.linkedin.com/in/',
            )
        ):
            raise HTTPException(400, 'Invalid LinkedIn link')
    if instagram:
        if not instagram.startswith(
            (
                'https://instagram.com/',
                'instagram.com/',
                'www.instagram.com/',
                'https://www.instagram.com/',
            )
        ):
            raise HTTPException(400, 'Invalid Instagram link')

    return links


def verify_admin_password_header(request: Request, auth_user: "User"):
    request_password = request.headers.get('X-Admin-Password')
    print(request_password, auth_user.password)
    if not request_password:
        raise HTTPException(400, 'Missing X-Admin-Password header')
    is_valid = verify_password(request_password, auth_user.password)
    if not is_valid:
        raise HTTPException(401, 'Invalid admin password')
