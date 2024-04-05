from datetime import datetime, timedelta, timezone
from functools import partial
from typing import Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from dundie.auth.models import TokenData
from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User
from dundie.utils.status import exp401
from dundie.security import verify_password

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    scope: str = 'access_token',
) -> str:
    """Creates a JWT Token from user data

    scope: access_token or refresh_token
    """

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode = data.copy()
    to_encode.update({'exp': expire, 'scope': scope})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


create_refresh_token = partial(create_access_token, scope='refresh_token')


def correct_authorization_header_syntax(request: Request):
    if authorization := request.headers.get('Authorization'):
        try:
            splited = authorization.split(' ')

            # Checks if the token was sent
            splited[1]

            if splited[0].lower() != 'bearer':
                raise HTTPException(
                    401, "Invalid authentication method. Use Bearer."
                )

        except IndexError:
            raise exp401('Invalid Authorization header format')


def authenticate_user(
    get_user: Callable, username: str, password: str
) -> User | None:
    """Authenticate the user"""

    user = get_user(username)
    if not user:
        return
    if not verify_password(password, user.password):
        return
    return user


def get_user(username, session: Session | None = None) -> User | None:
    """Get user from database"""
    stmt = select(User).where(User.username == username)

    if not session:
        with Session(engine) as session:
            return session.exec(stmt).first()
    else:
        return session.exec(stmt).first()


def get_current_user(
    _: None = Depends(correct_authorization_header_syntax),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
    fresh: bool = False,
) -> User:
    """Get the current user authenticated"""

    # Extract the token from the Authorization header
    # The header is in the format: `Bearer <token>`
    if request:
        if authorization := request.headers.get('Authorization'):
            try:
                token = authorization.split(' ')[1]
            except IndexError:
                raise exp401('Invalid Authorization header format')

    # Verify the token and get the username from the payload
    # The token is decoded using the SECRET_KEY and the ALGORITHM specified
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if not username:
            raise exp401('Token does not contain a valid username (sub)')

        token_data = TokenData(username=username)

    except JWTError:
        raise exp401('Could not decode token or token is invalid')

    # Get user from database if user exists
    user = get_user(username=token_data.username)
    if not user:
        raise exp401('User not found')

    # Check if user is fresh (token was issued recently) or if user is a
    # superuser, if not, raise an exception
    if fresh and (not payload['fresh'] and not user.superuser):
        raise exp401('Token is not fresh and user is not a superuser.')

    return user


async def get_user_if_change_password_is_allowed(
    *, request: Request, username: str, pwd_reset_token: str | None = None
) -> User:
    """
    Returns User if one of the conditions is met.

    - there is a valid pwd_reset_token passed in the url, or
    - authenticated user is superuser, or
    - authenticated user is the User
    """
    target_user = get_user(username)
    if not target_user:
        raise HTTPException(404, 'User not found')

    try:
        valid_pwd_reset_token = (
            get_current_user(token=pwd_reset_token or '') == target_user
        )
    except HTTPException:
        valid_pwd_reset_token = False

    try:
        current_user = get_current_user(token='', request=request)
    except HTTPException:
        current_user = False

    if any(
        [
            valid_pwd_reset_token,
            current_user and current_user.superuser,
            current_user and current_user.id == target_user.id,
        ]
    ):
        if (
            not current_user.superuser and
            target_user.last_password_change is not None
        ):

            # Checks if the password has been changed recently
            limit_seconds = settings.security.PWD_RESET_TIME_LIMIT_SECONDS
            now = datetime.now(timezone.utc)
            user_last_change = now - target_user.last_password_change
            if user_last_change.seconds < limit_seconds:
                raise HTTPException(
                    403,
                    "Your password has recently been changed, Try again later."
                )

        return target_user

    raise HTTPException(
        403, "You are not allowed to change this user's password"
    )


# Dependencies FASTAPI


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get the active user"""
    return current_user


async def user_is_superuser(
    current_user: User = Depends(get_current_user),
) -> bool:
    return current_user.superuser


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    """
    Validates user token

    This dependency validates the user token and returns the user if the token
    is valid. If the token is not valid, it raises an HTTPException with a 401
    status code.

    Args:
        token (str): The user token

    Returns:
        User: The user
    """
    user = get_current_user(token=token)
    return user


AuthenticatedUser: User = Depends(get_current_active_user)
SuperUser: User = Depends(user_is_superuser)
CanChangeUserPassword: User = Depends(get_user_if_change_password_is_allowed)
