from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dundie.db import ActiveSession
from dundie.models.user import User
from dundie.serializers import UserRequest, UserResponse, UserPatchRequest
from dundie.auth.functions import AuthenticatedUser
from dundie.utils.functions import apply_user_patch

router = APIRouter()


@router.get(
    '/',
    response_model=List[UserResponse],
    summary='List all users',
    dependencies=[AuthenticatedUser],
)
async def list_users(*, session: Session = ActiveSession):
    """
    List all users.

    Arguments:
    - session (Session): An active database session.

    Returns:
    - List[UserResponse]: A list of user responses containing user data.
    """
    # TODO: Order
    try:
        stmt = select(User)
        users = session.exec(stmt).all()
    except Exception as e:
        print(e)

    if not users:
        raise HTTPException(204, 'The user list is empty')

    return users


@router.get(
    '/{username}',
    response_model=UserResponse,
    summary='Get a user by username',
    dependencies=[AuthenticatedUser],
)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """
    Get a user by username.

    Args:
    - session (Session): An active session object for database operations.
    - username (str): The username of the user to retrieve.

    Returns:
    - UserResponse: A response containing the user information.

    Raises:
    - HTTPException: If the user with the specified username is not found
    (status code 404).
    """
    try:
        stmt = select(User).where(User.username == username)
        user = session.exec(stmt).first()
    except Exception as e:
        print(e)

    if not user:
        raise HTTPException(404, 'User not found')

    return user


@router.post(
    '/',
    response_model=UserResponse,
    status_code=201,
    summary='Creates a new user',
    dependencies=[],
)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """
    Creates a new user.

    Args:
    - session (Session): The active session to interact with the database.
    - user (UserRequest): The data representing the new user to be created.

    Returns:
    - User: The newly created user object.

    Raises:
    - HTTPException: If there is a constraint violation error during the
    database transaction.
    """
    # Checks if there is already a user with that username
    stmt = select(User).where(User.username == user.username)
    if session.exec(stmt).first():
        raise HTTPException(409, 'Username alredy in use')

    # Checks if there is already a user with that email
    stmt = select(User).where(User.email == user.email)
    if session.exec(stmt).first():
        raise HTTPException(409, 'Email alredy in use')

    db_user = User.from_orm(user)
    session.add(db_user)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(500, 'Database IntegrityError')

    session.refresh(db_user)

    return db_user


@router.patch(
    '/{username}',
    summary='Updates partialy the user data',
    response_model=UserResponse
)
async def update_bio_and_avatar(
    *,
    username: str,
    session: Session = ActiveSession,
    patch_data: UserPatchRequest,
    current_user: User = AuthenticatedUser
):
    """Update an already registered user"""

    # Checks if the sent user exists
    stmt = select(User).where(User.username == username)
    if not (user := session.exec(stmt).first()):
        raise HTTPException(404, 'User not found')

    # Checks if the current_user id differs from the URL user id
    # and if the current_user is a superuser
    if (
        current_user.id != user.id
        and not current_user.superuser
    ):
        raise HTTPException(403, 'Permission denied to update this user')

    # Apply updates to the user instance
    apply_user_patch(user, patch_data)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        print(e)

    return user
