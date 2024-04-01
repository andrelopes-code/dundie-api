from fastapi import APIRouter

from .user import router as user_router
from .auth import router as auth_router

main_router = APIRouter()

main_router.include_router(router=user_router, prefix='/user', tags=['User'])
main_router.include_router(router=auth_router, tags=['Auth'])
