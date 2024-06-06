from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.websocket.app import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('server is starting')
    await init_db()
    yield
    print('server is stopping')


app = FastAPI(
    title="ManagerVM",
    version="1.0.0",
    description="Manager VM service",
    lifespan=lifespan,
)
app.include_router(websocket_router)

