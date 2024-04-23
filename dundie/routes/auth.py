from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from dundie.auth.functions import (
    authenticate_user,
    create_both_tokens,
    get_user,
    validate_token,
    validate_token_signature,
)
from dundie.auth.models import Token
from dundie.models.user import User
from dundie.utils.status import exp401

router = APIRouter()


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Generate access and refresh tokens for authentication."""
    user = authenticate_user(get_user, form_data.username, form_data.password)
    if not user or not isinstance(user, User) or not user.is_active:
        raise exp401('Incorrect username or password')

    # Generating both access and refresh tokens for the user session
    access_token, refresh_token = create_both_tokens(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )


@router.post('/refresh_token', response_model=Token)
async def refresh_token(request: Request):
    """Obtain a new access token using a refresh token."""

    token = request.cookies.get('refresh_token') or request.headers.get(
        'x-refresh-token'
    )

    if not token:
        raise HTTPException(403, 'No refresh token')

    user = await validate_token(token=token)

    # Generating both access and refresh tokens for the user session
    access_token, refresh_token = create_both_tokens(user)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )


@router.get('/token/validate')
async def check_is_valid_token(request: Request):
    """
    Validate a token by checking its signature and returning a
    success message if it is valid.

    Args:
        request (Request): The request object containing the header
        'x-access-token' to validate token.

    Returns:
        dict: A dict with a success message if the token is valid.

    """

    token = request.headers.get('x-access-token')

    result = await validate_token_signature(token)
    if result.get('sub'):
        return {'detail': result}

    raise HTTPException(401, 'Unauthorized')
