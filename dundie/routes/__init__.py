from fastapi import APIRouter

from .admin import router as admin_router
from .auth import router as auth_router
from .transaction import router as transaction_router
from .user import router as user_router

main_router = APIRouter(redirect_slashes=False)

main_router.include_router(router=user_router, prefix='/user', tags=['User'])

main_router.include_router(router=auth_router, tags=['Auth'])

main_router.include_router(router=transaction_router, tags=['Transaction'])

main_router.include_router(
    prefix='/admin', router=admin_router, tags=['Admin']
)
