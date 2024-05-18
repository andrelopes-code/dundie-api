import re
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dundie.auth.functions import (
    AuthenticatedUser,
    CanChangeUserPassword,
    create_both_tokens,
    get_user,
)
from dundie.db import ActiveSession
from dundie.models import User
from dundie.security import verify_password
from dundie.serializers import (
    EmailRequest,
    UserAvatarPatchRequest,
    UserLinksPatchRequest,
    UsernamesResponse,
    UserPasswordPatchRequest,
    UserPrivateProfileResponse,
    UserProfilePatchRequest,
    UserPublicProfileResponse,
    UserResponse,
)
from dundie.tasks.user import try_to_send_password_reset_email
from dundie.utils.utils import apply_user_links_patch, apply_user_profile_patch

router = APIRouter()


# * PATCH /user/links ~ Updates the user profile links
@router.patch(
    '/links',
    summary="Updates the authenticated user profile links",
    tags=['Profile'],
)
async def patch_user_profile_links(
    user_link_data: UserLinksPatchRequest,
    *,
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """
    This function handles the PATCH request to update the links of the user
    profile. It checks if the user making the request exists and has the
    correct credentials. If the user exists and has the correct credentials,
    it updates the user data accordingly.
    """
    apply_user_links_patch(current_user, user_link_data)
    session.add(current_user)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(500, str(e))

    return {'detail': 'profile updated!'}


# * GET /user/profile ~ Gets the authenticated user profile
@router.get(
    '/profile',
    summary="Gets the authenticated user profile",
    response_model=UserPrivateProfileResponse,
    tags=['Profile'],
)
async def get_private_user_profile_data(*, user: User = AuthenticatedUser):
    """
    This function handles the GET request to retrieve the profile data of the
    authenticated user. It checks if the user making the request exists and
    has the correct credentials. If the user exists and has the correct
    credentials, it returns the user data as a UserPrivateProfileResponse
    object.
    """
    return user.model_dump()


# * /user/profile/avatar ~ Updates avatar image link for the authenticated user
@router.patch(
    '/profile/avatar',
    tags=['Profile'],
    summary='Uploads a new avatar image link for the authenticated user',
)
async def upload_avatar_image_link(
    *,
    avatar_image_link: UserAvatarPatchRequest,
    user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """
    This function handles the PATCH request to update the avatar image link of
    the authenticated user, it reiceves a link to the image and updates the
    user's avatar link.
    """
    # ? It is a simple solution for the problem
    user.avatar = avatar_image_link.avatar_url
    try:
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            400, 'Something went wrong while updating the avatar link'
        )

    return {'detail': 'avatar updated!'}


# * /user/public/{username} ~ Gets public user profile
@router.get(
    '/public/{username}',
    summary="Gets public user profile",
    response_model=UserPublicProfileResponse,
    dependencies=[AuthenticatedUser],
    tags=['Profile'],
)
async def get_public_user_profile_data(
    username: str, *, session: Session = ActiveSession
):
    """
    This function handles the GET request to retrieve the profile data of the
    taget user. It checks if the user making the request exists and has the
    correct credentials. If the user exists and has the correct credentials,
    it returns the target user data as a UserPublicProfileResponse object.
    """
    target_user = get_user(username=username, session=session)
    return target_user.model_dump()


# * PATCH /user/profile ~ Updates the authenticated user profile
@router.patch(
    '/profile',
    summary="Updates the authenticated user profile data",
    tags=['Profile'],
)
async def patch_user_profile_data(
    user_data: UserProfilePatchRequest,
    *,
    current_user: User = AuthenticatedUser,
    session: Session = ActiveSession,
):
    """
    This function handles the PATCH request to update the profile data of the
    authenticated user. It checks if the user making the request exists and
    has the correct credentials. If the user exists and has the correct
    credentials, it updates the user data accordingly.

    If the username is changed, it also generates new access and refresh tokens
    for the user session.
    """
    old_username = current_user.username
    apply_user_profile_patch(current_user, user_data)

    session.add(current_user)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(500, str(e))

    if user_data.username != old_username:
        session.refresh(current_user)
        # Generating both access and refresh tokens for the user session
        access_token, refresh_token = create_both_tokens(current_user)
        return {
            "detail": "profile updated!",
            "refresh": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    return {"detail": "profile updated!"}


# * GET /user ~ Gets a list of all users
@router.get(
    '',  # ROOT '/'
    summary='List all users',
    response_model=Page[UserResponse],
)
async def list_all_users_in_db(
    request: Request,
    *,
    session: Session = ActiveSession,
    current_user: User = AuthenticatedUser,
    params: Params = Depends(),
):
    """
    This function handles the GET request to retrieve a list of all users
    registered in the system. It requires authentication for access.
    Upon successful authentication, it queries the database to fetch all
    user records and returns them as a list of UserResponse objects.
    If query params to 'sort' (sort=asc) are passed, it will do the query
    with the sort method: descending, ascending, etc.
    """

    # Query users who are not private or disabled
    stmt = select(User).where(
        and_(User.is_active == True, User.private == False)  # noqa: E712
    )

    try:
        # Paginates the user list response
        return paginate(query=stmt, params=params, session=session)
    except Exception as e:
        print(e)

    return {'detail': 'failed'}


# * GET /user/names ~ Gets a list of all usernames
@router.get(
    '/names',
    summary='List all users',
    dependencies=[],
    response_model=List[UsernamesResponse],
)
async def get_usernames(
    query: str | None = None,
    session: Session = ActiveSession,
):
    if not query:
        return []

    stmt = (
        select(User.username, User.name)
        .where(User.username.like(f'%{query}%'))
        .filter(and_(User.is_active == True, User.private == False))  # noqa: E712 E501
        .limit(10)
    )
    users = session.exec(stmt).all()
    return users


# * POST /{username}/password ~ Changes the specified user password
@router.post(
    '/{username}/password',
    summary='Changes the specified user password',
    dependencies=[],
    response_model=UserResponse,
)
async def change_user_password(
    username: str,
    patch_data: UserPasswordPatchRequest,
    session: Session = ActiveSession,
    user: User = CanChangeUserPassword,
):
    """
    This function handles the POST request to change the password of the
    specified user. Authentication is required to access this endpoint.
    It verifies that the new password is different from the current password
    before updating it in the database.
    """

    # Checks if the new password is the same as the current password
    if verify_password(patch_data.password, user.password):
        raise HTTPException(400, 'New password matches the current one')

    regex = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$"
    if not re.match(regex, patch_data.password):
        raise HTTPException(
            400,
            'Password must be at least 8 characters long, contain at'
            + 'least one upper and lower case letter and one number',
        )

    # Change the password
    user.password = patch_data.hashed_password
    session.add(user)

    try:
        session.commit()
        session.refresh(user)

    except IntegrityError as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'Database IntegrityError')

    return user


# * POST /pwd_reset_token ~ Send an email to reset the password
@router.post(
    '/pwd_reset_token',
    summary='Send an email to reset the password',
)
async def send_password_reset_token(
    email_request: EmailRequest,
    background_task: BackgroundTasks,
):
    """
    This function handles the POST request to send a password reset token to
    the specified email address. It triggers the sending of an email
    containing the token required for resetting the password.
    TODO:
        create a SMTP server.
    """

    background_task.add_task(
        try_to_send_password_reset_email, email=email_request.email
    )

    return {
        'detail': 'If we have found a user with that email, '
        + "we've sent a password reset token to it."
    }
