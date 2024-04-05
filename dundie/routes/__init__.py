from fastapi import APIRouter

from .auth import router as auth_router
from .user import router as user_router
from .transaction import router as transaction_router

main_router = APIRouter(redirect_slashes=False)

main_router.include_router(
    router=user_router,
    prefix='/user',
    tags=['User']
)

main_router.include_router(
    router=auth_router,
    tags=['Auth']
)

main_router.include_router(
    router=transaction_router,
    prefix='/transaction',
    tags=['Transaction']
)
