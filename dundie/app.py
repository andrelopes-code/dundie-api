from fastapi import FastAPI

from dundie.middlewares import configure as cfg_middlewares
from dundie.routes import main_router

app = FastAPI(
    title='dundie', version='0.1.0', description='Dundie is a rewards API.'
)


cfg_middlewares(app)
app.include_router(main_router)
