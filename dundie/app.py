from fastapi import FastAPI

from dundie.routes.user import router as user_router

app = FastAPI(
    title='dundie', version='0.1.0', description='Dundie is a rewards API.'
)

# Routers
app.include_router(router=user_router, prefix='/user', tags=['User'])
