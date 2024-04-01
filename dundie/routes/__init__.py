from fastapi import APIRouter

from dundie.routes.user import router as user_router

main_router = APIRouter()

main_router.include_router(router=user_router, prefix='/user', tags=['User'])
