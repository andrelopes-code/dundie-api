from fastapi import FastAPI, Request
import time
from dundie.middlewares import configure as cfg_middlewares
from dundie.routes import main_router

app = FastAPI(
    title='dundie', version='0.1.0', description='Dundie is a rewards API.'
)


cfg_middlewares(app)
app.include_router(main_router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Process time: {process_time}")
    response.headers["X-Process-Time"] = str(process_time)
    return response
