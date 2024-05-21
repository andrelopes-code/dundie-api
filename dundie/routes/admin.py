from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select
import re
from dundie.utils.utils import (
    apply_product_patch,
    check_password_complexity,
    get_utcnow,
)
from dundie.auth.functions import SuperUser
from dundie.config import settings
from dundie.utils.utils import apply_user_patch, verify_admin_password_header
from dundie.controllers import create_user_and_balance
from dundie.db import ActiveSession
from dundie.models import User, Orders, Products
from dundie.security import verify_password
from dundie.serializers.admin import (
    UserAdminResponse,
    UserChangeVisibilityRequest,
    FullUserPatchRequest,
)
from dundie.serializers.user import UserRequest, UserResponse
from dundie.serializers.shop import (
    ProductRequest,
    ProductResponse,
    ProductUpdateRequest,
)

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
    response_model=UserResponse,
)
async def create_new_user_in_db(
    *,
    request: Request,
    new_user_data: UserRequest,
    auth_user: User = SuperUser,
    session: Session = ActiveSession,
):
    """Creates a new user in the database"""

    verify_admin_password_header(request, auth_user)

    # Checks if there is already a user with that username
    stmt = select(User).where(User.username == new_user_data.username)
    if (
        session.exec(stmt).first()
        or new_user_data.username in settings.PRIVATE_USERNAMES
    ):
        raise HTTPException(409, 'Username alredy in use')

    # Checks if there is already a user with that email
    stmt = select(User).where(User.email == new_user_data.email)
    if session.exec(stmt).first():
        raise HTTPException(409, 'Email alredy in use')

    db_user = create_user_and_balance(user_data=new_user_data, session=session)

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

    # check the admin user password
    is_admin_password_valid = verify_password(
        data.password, current_user.password
    )

    if not is_admin_password_valid:
        raise HTTPException(401, 'Invalid admin password')

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


@router.get(
    '/{username}',
    summary='Get a user by username [ADMIN]',
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


@router.patch(
    '/{username}',
    summary='Updates a user by username [ADMIN]',
)
async def update_user_by_username(
    *,
    username: str,
    admin_user: User = SuperUser,
    patch_data: FullUserPatchRequest,
    session: Session = ActiveSession,
):
    """Updates a user by username"""

    # Check if the admin user password is valid
    is_admin_password_valid = verify_password(
        patch_data.admin_password, admin_user.password
    )
    if not is_admin_password_valid:
        raise HTTPException(401, 'Invalid admin password')

    # Check if the user exists
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    if not user:
        raise HTTPException(404, 'User not found')

    if patch_data.new_password:
        # Checks if the new password is the same as the current password
        if verify_password(patch_data.new_password, user.password):
            raise HTTPException(400, 'New password matches the current one')

        # Checks if the new password is complex enough
        check_password_complexity(patch_data.new_password)

        user.password = patch_data.hashed_password

    # ignore passwords from the patch data and apply it to the user
    apply_user_patch(
        user, patch_data, ignore=['new_password', 'admin_password']
    )

    try:
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'An error occurred while updating the user')

    return {'detail': f'user {username} updated'}


@router.get(
    '/shop/orders',
    summary='List all orders [ADMIN]',
    dependencies=[SuperUser],
)
async def get_orders(
    session: Session = ActiveSession,
    params: Params = Depends(),
):
    """Returns all orders"""

    stmt = select(Orders).order_by(Orders.status.desc())
    try:
        # Paginates the user list response
        return paginate(query=stmt, params=params, session=session)
    except Exception as e:
        print(e)

    return {'detail': 'failed to return orders'}


@router.post(
    '/shop/product',
    summary='Creates a new product [ADMIN]',
    response_model=ProductResponse,
)
async def create_product(
    request: Request,
    product: ProductRequest,
    auth_user: User = SuperUser,
    session: Session = ActiveSession,
):
    """Creates a new product"""

    # Check if the admin user password is valid
    verify_admin_password_header(request, auth_user)

    new_product = Products(
        name=product.name,
        description=product.description,
        image=product.image,
        price=product.price,
    )

    session.add(new_product)
    try:
        session.commit()
        session.refresh(new_product)
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'An error occurred w creating the product')

    return new_product


@router.patch(
    '/shop/product',
    summary='Updates a product [ADMIN]',
    response_model=ProductResponse,
)
async def update_product(
    request: Request,
    patch_data: ProductUpdateRequest,
    auth_user: User = SuperUser,
    session: Session = ActiveSession,
):
    """Updates a product"""

    # Check if the admin user password is valid
    verify_admin_password_header(request, auth_user)

    stmt = select(Products).where(Products.id == patch_data.id)
    product = session.exec(stmt).first()
    if not product:
        raise HTTPException(404, 'Product not found')

    # apply the patch data to the product
    apply_product_patch(product, patch_data)
    product.updated_at = get_utcnow()

    try:
        session.add(product)
        session.commit()
        session.refresh(product)
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'An error occurred w updating the product')

    return product


@router.delete(
    '/shop/product',
    summary='Deletes a product [ADMIN]',
)
async def delete_product(
    request: Request,
    id: int,
    user: User = SuperUser,
    session: Session = ActiveSession,
):
    """Deletes a product"""

    # Check if the admin user password is valid
    verify_admin_password_header(request, user)

    stmt = select(Products).where(Products.id == id)
    product = session.exec(stmt).first()
    if not product:
        raise HTTPException(404, 'Product not found')

    try:
        session.delete(product)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(500, 'An error occurred w deleting the product')

    return {'detail': 'product deleted successfully'}
