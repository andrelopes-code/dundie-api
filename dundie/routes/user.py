from typing import List

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.exceptions import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dundie.auth.functions import (
    AuthenticatedUser,
    CanChangeUserPassword,
    SuperUser,
    create_both_tokens,
    get_user,
)
from dundie.config import settings
from dundie.controllers import create_user_and_balance
from dundie.db import ActiveSession
from dundie.models import User
from dundie.routes.descriptions import (
    CHANGE_USER_PASSWORD_DESC,
    CREATE_USER_DESC,
    GET_USER_BY_USERNAME_DESC,
    LIST_USERS_DESC,
    PASSWORD_RESET_EMAIL_DESC,
    PATCH_USER_DATA_DESC,
)
from dundie.security import verify_password
from dundie.serializers import (
    EmailRequest,
    UserLinksPatchRequest,
    UserPasswordPatchRequest,
    UserPatchRequest,
    UserPrivateProfileResponse,
    UserProfilePatchRequest,
    UserPublicProfileResponse,
    UserRequest,
    UserResponse,
    UsernamesResponse,
)
from dundie.tasks.user import try_to_send_password_reset_email
from dundie.utils.utils import (
    apply_user_links_patch,
    apply_user_patch,
    apply_user_profile_patch,
)


router = APIRouter(redirect_slashes=True)


@router.patch(
    '/links',
    summary="Updates the authenticated user profile links"
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


@router.get(
    '/profile',
    summary="Gets the authenticated user profile",
    response_model=UserPrivateProfileResponse,
)
async def get_private_user_profile_data(
    *,
    user: User = AuthenticatedUser
):
    """
    This function handles the GET request to retrieve the profile data of the
    authenticated user. It checks if the user making the request exists and
    has the correct credentials. If the user exists and has the correct
    credentials, it returns the user data as a UserPrivateProfileResponse
    object.
    """
    return user.model_dump()


@router.get(
    '/public/{username}',
    summary="Gets the authenticated user profile",
    response_model=UserPublicProfileResponse,
    dependencies=[AuthenticatedUser],
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


@router.patch(
    '/profile',
    summary="Updates the authenticated user profile data",
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


@router.get(
    '',  # ROOT '/'
    summary='List all users',
    description=LIST_USERS_DESC,
    dependencies=[AuthenticatedUser],
    response_model=List[UserResponse],
)
async def list_all_users_in_db(
    request: Request, *, session: Session = ActiveSession
):
    """
    This function handles the GET request to retrieve a list of all users
    registered in the system. It requires authentication for access.
    Upon successful authentication, it queries the database to fetch all
    user records and returns them as a list of UserResponse objects.
    If query params to 'sort' (sort=asc) are passed, it will do the query
    with the sort method: descending, ascending, etc.

    Args:
        - request: the Request object.
        - session (Session, optional): An active session to interact with the
        database. Defaults to ActiveSession.

    Returns:
        List[UserResponse]: A list of user objects containing user details
        such as username, email, etc.

    Raises:
        HTTPException: An HTTP exception with status code 204 is raised if the
        user list is empty.
    """

    # Query users who are not private or disabled
    stmt = select(User).where(
        and_(User.is_active == True, User.private == False)  # noqa: E712
    )

    try:
        users = session.exec(stmt).all()
    except Exception as e:
        print(e)

    if not users:
        raise HTTPException(204, 'The user list is empty')

    return users


@router.get(
    '/names',  # ROOT '/'
    summary='List all users',
    description=LIST_USERS_DESC,
    dependencies=[],
    response_model=List[UsernamesResponse],
)
async def get_usernames(
    query: str | None = None,
    session: Session = ActiveSession,
):
    if not query:
        return []
    # !
    stmt = (
        select(User.username, User.name)
        .where(User.username.like(f'%{query}%'))
    ).limit(10)
    users = session.exec(stmt).all()
    return users


@router.get(
    '/{username}',
    summary='Get a user by username',
    description=GET_USER_BY_USERNAME_DESC,
    dependencies=[AuthenticatedUser],
    response_model=UserResponse,
)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """
    This function handles the GET request to retrieve a user by their username.
    It requires authentication for access. Upon successful authentication,
    it queries the database to fetch the user record corresponding to the
    provided username and returns it as a UserResponse object.

    Args:
        - session (Session, optional): An active session to interact with the
        database. Defaults to ActiveSession.
        - username (str): The username of the user to retrieve.

    Returns:
        UserResponse: An object containing details of the user such as
        username, email, etc.

    Raises:
        HTTPException: An HTTP exception with status code 404 is raised if
        the user corresponding to the provided username is not found.
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
    '',  # ROOT '/'
    summary='Creates a new user',
    description=CREATE_USER_DESC,
    status_code=201,
    dependencies=[SuperUser],
    response_model=UserResponse,
)
async def create_new_user_in_db(
    *, session: Session = ActiveSession, user: UserRequest
):
    """
    This function handles the POST request to create a new user. Access is
    restricted to super users only. It validates the input data and ensures
    that the username and email are unique before adding the new user to
    the database.

    Args:
        - session (Session, optional): An active session to interact with the
        database. Defaults to ActiveSession.
        - user (UserRequest): An object containing the details of the user to
        be created.

    Returns:
        UserResponse: An object containing details of the newly created user
        such as username, email, etc.

    Raises:
        HTTPException:
        - An HTTP exception with status code 409 is raised if the provided
        username or email is already in use.
        - An HTTP exception with status code 500 is raised if there is an
        integrity error while committing to the database.
    """

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


@router.patch(
    '/{username}',
    summary='Updates partialy the user data',
    description=PATCH_USER_DATA_DESC,
    dependencies=[AuthenticatedUser],
    response_model=UserResponse,
)
async def update_bio_and_avatar(
    *,
    username: str,
    session: Session = ActiveSession,
    patch_data: UserPatchRequest,
    current_user: User = AuthenticatedUser,
):
    """
    This function handles the PATCH request to update partial data of an
    already registered user. Authentication is required to access this
    endpoint. It checks if the user making the request exists and has the
    necessary permissions to perform the update. If the user is not a super
    user, they can only update their own data. Super users can update any
    user's data.

    Args:
        - username (str): The username of the user whose data needs to be
        updated.
        - session (Session, optional): An active session to interact with the
        database. Defaults to ActiveSession.
        - patch_data (UserPatchRequest): An object containing the partial data
        to be updated for the user.
        - current_user (User): The currently authenticated user. Defaults to
        AuthenticatedUser.

    Returns:
        UserResponse: An object containing the updated details of the user
        such as username, email, etc.

    Raises:
        HTTPException:
        - An HTTP exception with status code 404 is raised if the user
        corresponding to the provided username is not found.
        - An HTTP exception with status code 403 is raised if the current
        user does not have permission to update the user data.
        - An HTTP exception with status code 500 is raised if there is an
        integrity error while committing to the database.
    """

    # Checks if the sent user exists
    stmt = select(User).where(User.username == username)
    if not (user := session.exec(stmt).first()):
        raise HTTPException(404, 'User not found')

    # Checks if the current_user id differs from the URL user id
    # and if the current_user is a superuser
    if current_user.id != user.id and not current_user.superuser:
        raise HTTPException(403, 'Permission denied to update this user')

    # Apply updates to the user instance
    apply_user_patch(user, patch_data)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except IntegrityError as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'Database IntegrityError')

    return user


@router.post(
    '/{username}/password',
    summary='Changes the specified user password',
    description=CHANGE_USER_PASSWORD_DESC,
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

    Args:
        - username (str): The username of the user whose password needs to
        be changed.
        - patch_data (UserPasswordPatchRequest): An object containing the
        new hashed password.
        - session (Session, optional): An active session to interact with
        the database. Defaults to ActiveSession.
        - user (User): The user whose password is being changed. Defaults
        to CanChangeUserPassword.

    Returns:
        UserResponse: An object containing the updated details of the user
        such as username, email, etc.

    Raises:
        HTTPException:
        - An HTTP exception with status code 400 is raised if the new
        password matches the current one.
        - An HTTP exception with status code 500 is raised if there is an
        integrity error while committing to the database.

    TODO:
        Add a password change limit and a User.last_password_change attr
    """

    # Checks if the new password is the same as the current password
    if verify_password(patch_data.password, user.password):
        raise HTTPException(400, 'New password matches the current one')

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


@router.post(
    '/pwd_reset_token',
    summary='Send an email to reset the password',
    description=PASSWORD_RESET_EMAIL_DESC,
)
async def send_password_reset_token(
    email_request: EmailRequest,
    background_task: BackgroundTasks,
):
    """
    This function handles the POST request to send a password reset token to
    the specified email address. It triggers the sending of an email
    containing the token required for resetting the password.

    Args:
    email_request (EmailRequest): An object containing the email address to
    which the password reset token will be sent.

    Returns:
        dict: A dictionary containing a message indicating the status of the
        password reset token email delivery.

    TODO:
        create a SMTP server.
    """

    background_task.add_task(
        try_to_send_password_reset_email, email=email_request.email
    )

    return {
        'message': 'If we have found a user with that email, '
        + "we've sent a password reset token to it."
    }
