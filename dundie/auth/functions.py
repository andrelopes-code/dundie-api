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
from dundie.security import verify_password
from dundie.utils.status import exp401

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes

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
        expire = datetime.now(timezone.utc) + timedelta(minutes=5)

    to_encode = data.copy()
    to_encode.update({'exp': expire, 'scope': scope})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def create_both_tokens(
    user: User,
):
    """Create both access and refresh tokens for the user session"""
    # Creates an access token for the authenticated user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username, 'dept': user.dept, 'fresh': False},
        expires_delta=access_token_expires,
    )

    # Creates a refresh token for the authenticated user
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={'sub': user.username, 'dept': user.dept},
        expires_delta=refresh_token_expires,
    )

    return access_token, refresh_token


create_refresh_token = partial(create_access_token, scope='refresh_token')


def correct_authorization_header_syntax(request: Request):
    if authorization := request.headers.get('authorization'):
        try:
            splited = authorization.split(' ')

            # Checks if the token was sent
            splited[1]

            if splited[0].lower() != 'bearer':
                raise HTTPException(
                    401, "Invalid authentication method. Use Bearer."
                )

        except IndexError:
            raise exp401('Invalid authorization header format')


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
    # Extract the token from the authorization header
    # The header is in the format: `Bearer <token>`
    if request:
        if authorization := request.headers.get('authorization'):
            try:
                token = authorization.split(' ')[1]
            except IndexError:
                raise exp401('Invalid authorization header format')

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
        if pwd_reset_token:
            valid_pwd_reset_token = (
                get_current_user(token=pwd_reset_token or '') == target_user
            )
        else:
            valid_pwd_reset_token = False
    except HTTPException:
        # if pwd_reset_token sent is invalid
        raise HTTPException(403, 'Possibly the token has expired')

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
        # ! CHECK FOR PASSWORD CHANGE, NOT FOR PWD RESET
        if (
            current_user and not current_user.superuser
        ) and target_user.last_password_change is not None:

            # Checks if the password has been changed recently
            limit_seconds = settings.security.PWD_RESET_TIME_LIMIT_SECONDS
            now = datetime.now(timezone.utc)
            user_last_change = now - target_user.last_password_change
            if user_last_change.seconds < limit_seconds:
                raise HTTPException(
                    403,
                    "Your password has recently been changed, Try again later",
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
    if not current_user.superuser:
        raise HTTPException(401, 'You are not a Super User!')
    return current_user


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


async def validate_token_signature(token: str | None):

    if token is None:
        raise exp401('No token sent')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if not username:
            raise exp401('Token does not contain a valid username (sub)')

        return payload

    except JWTError:
        raise exp401('Could not decode token or token is invalid')

    except Exception as e:
        print(e)


AuthenticatedUser: User = Depends(get_current_active_user)
SuperUser: User = Depends(user_is_superuser)
CanChangeUserPassword: User = Depends(get_user_if_change_password_is_allowed)
