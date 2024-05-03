import time

from fastapi import FastAPI, Request

from dundie.middlewares import configure as cfg_middlewares
from dundie.routes import main_router
from dundie.websocket.chat import router as chat_router

app = FastAPI(
    title='dundie', version='0.1.0', description='Dundie is a rewards API.'
)


cfg_middlewares(app)
app.include_router(main_router)
app.include_router(chat_router)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f'\n\033[1;31mProcess time: {process_time}\033[m')
    response.headers['X-Process-Time'] = str(process_time)
    return response
