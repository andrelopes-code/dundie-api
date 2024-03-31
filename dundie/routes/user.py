from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from dundie.db import ActiveSession
from dundie.models.user import User
from dundie.serializers import UserRequest, UserResponse
from dundie.routes.status import get_status

from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.get('/', response_model=List[UserResponse], summary='List all users')
async def list_users(*, session: Session = ActiveSession):
    """
    List all users.

    Arguments:
    - session (Session): An active database session.

    Returns:
    - List[UserResponse]: A list of user responses containing user data.
    """
    # TODO: Order
    stmt = select(User)
    users = session.exec(stmt).all()

    if not users:
        raise HTTPException(204, 'The user list is empty')

    return users


@router.get(
    '/{username}',
    response_model=UserResponse,
    summary='Get a user by username.',
    responses={
        404: get_status('Not found')
        },
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
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.post(
    '/',
    response_model=UserResponse,
    status_code=201,
    summary='Creates a new user.',
    responses={
        409: get_status('Conflict')
        },
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
    db_user = User.from_orm(user)
    session.add(db_user)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "An error occurred when registering the user")

    session.refresh(db_user)

    return db_user
