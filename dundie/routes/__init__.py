from fastapi import APIRouter

from .admin import router as admin_router
from .auth import router as auth_router
from .transaction import router as transaction_router
from .user import router as user_router
from .post import router as post_router
from .testing import router as testing_router
from .shop import router as shop_router
from .others import router as others_router

main_router = APIRouter(redirect_slashes=False)

main_router.include_router(router=user_router, prefix='/user', tags=['User'])

main_router.include_router(router=auth_router, tags=['Auth'])

main_router.include_router(router=transaction_router, tags=['Transaction'])

main_router.include_router(
    prefix='/admin', router=admin_router, tags=['Admin']
)

main_router.include_router(router=post_router, tags=['Post'])

main_router.include_router(router=testing_router, tags=['Test'])

main_router.include_router(router=shop_router, tags=['Shop'])

main_router.include_router(router=others_router, tags=['Other'])
