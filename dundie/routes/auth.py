from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from rich import print as bprint

from dundie.auth.functions import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_user,
    validate_token,
)
from dundie.auth.models import Token
from dundie.config import settings
from dundie.models.user import User
from dundie.utils.status import exp401

ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes

router = APIRouter()


@router.post('/token', response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Generate access and refresh tokens for authentication."""

    user = authenticate_user(get_user, form_data.username, form_data.password)
    if not user or not isinstance(user, User):
        raise exp401('Incorrect username or password')

    # Creates an access token for the authenticated user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username, 'fresh': False},
        expires_delta=access_token_expires,
    )

    # Creates a refresh token for the authenticated user
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={'sub': user.username}, expires_delta=refresh_token_expires
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        expires=datetime.now(timezone.utc) + refresh_token_expires,
        httponly=True,
    )

    response.headers.append("Access-Control-Allow-Credentials", "true")
    response.headers.append("Access-Control-Allow-Methods", "*")
    response.headers.append("Access-Control-Allow-Origins", "*")

    return Token(access_token=access_token, token_type="Bearer")


@router.post('/refresh_token', response_model=Token)
async def refresh_token(request: Request, response: Response):
    """Obtain a new access token using a refresh token."""

    bprint(request.cookies)

    token = request.cookies.get('refresh_token')
    if not token:
        raise HTTPException(403, 'No refresh token')

    user = await validate_token(token=token)

    # Generating an access token for the user session with specific user data
    # and setting its expiration time.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username, 'fresh': True},
        expires_delta=access_token_expires,
    )

    # Generating a refresh token for the user session with specific user data
    # and defining its expiration time.
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={'sub': user.username}, expires_delta=refresh_token_expires
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        expires=datetime.now(timezone.utc) + refresh_token_expires,
        httponly=True,
    )

    response.headers.append("Access-Control-Allow-Credentials", "true")
    response.headers.append("Access-Control-Allow-Methods", "*")

    return Token(access_token=access_token, token_type="Bearer")
