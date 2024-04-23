from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from dundie.auth.functions import SuperUser
from dundie.config import settings
from dundie.controllers import create_user_and_balance
from dundie.db import ActiveSession
from dundie.models import User
from dundie.security import verify_password
from dundie.serializers.admin import (
    UserAdminResponse,
    UserChangeVisibilityRequest,
)
from dundie.serializers.user import UserRequest, UserResponse

# TODO: VALIDATE IF THE TOKEN IS FRESH
router = APIRouter()


@router.get(
    '/user',
    summary='List all users [ADMIN]',
    dependencies=[SuperUser],
    response_model=Page[UserAdminResponse],
)
async def list_all_users_in_db(
    *,
    session: Session = ActiveSession,
    current_user: User = SuperUser,
    params: Params = Depends(),
):
    """Returns a page with a user list"""

    query = select(User).order_by(User.name)

    try:
        # Paginates the user list response
        return paginate(query=query, params=params, session=session)
    except Exception as e:
        print(e)

    return {'detail': 'failed to return users'}


@router.post(
    '/user',
    summary='Creates a new user [ADMIN]',
    status_code=201,
    dependencies=[SuperUser],
    response_model=UserResponse,
)
async def create_new_user_in_db(
    *, session: Session = ActiveSession, user: UserRequest
):
    """Creates a new user in the database"""

    # Checks if there is already a user with that username
    stmt = select(User).where(User.username == user.username)
    if (
        session.exec(stmt).first()
        or user.username in settings.PRIVATE_USERNAMES
    ):
        raise HTTPException(409, 'Username alredy in use')

    # Checks if there is already a user with that email
    stmt = select(User).where(User.email == user.email)
    if session.exec(stmt).first():
        raise HTTPException(409, 'Email alredy in use')

    db_user = create_user_and_balance(user_data=user, session=session)

    return db_user


@router.put(
    '/user/visibility',
    summary='Deletes a user [ADMIN]',
    dependencies=[SuperUser],
)
async def change_user_visibility_by_username(
    data: UserChangeVisibilityRequest,
    current_user: User = SuperUser,
    session: Session = ActiveSession,
):
    """Changes the visibility of a user by username"""

    # TODO: VALIDATE IF THE TOKEN IS FRESH

    is_valid = verify_password(data.password, current_user.password)

    if not is_valid:
        print(is_valid, current_user.password, data.password)
        raise HTTPException(401, 'Invalid password')

    stmt = select(User).where(User.username == data.username)
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(404, 'User not found')

    # enable the user if it was disabled
    if data.enable:
        user.is_active = True
        session.add(user)
        session.commit()
        return {'detail': f'user {data.username} activated'}

    # disable the user if it was enabled
    if data.disable:
        user.is_active = False
        session.add(user)
        session.commit()
        return {'detail': f'user {data.username} deactivated'}

    # delete the user if it was not disabled
    session.delete(user)
    session.commit()
    return {'detail': f'user {data.username} deleted!'}


@router.get(
    '/{username}',
    summary='Get a user by username',
    dependencies=[SuperUser],
    response_model=UserResponse,
)
async def get_full_user_data_by_username(
    *, session: Session = ActiveSession, username: str
):
    """Returns a full user data by username"""

    try:
        stmt = select(User).where(User.username == username)
        user = session.exec(stmt).first()
    except Exception as e:
        print(e)

    if not user:
        raise HTTPException(404, 'User not found')

    return user
