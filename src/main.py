
from fastapi import FastAPI

from src.config import settings
from src.websocket.app import router as websocket_router


app = FastAPI(
    title="ManagerVM",
    version="1.0.0",
    description="Manager VM service",
)
app.include_router(websocket_router)


if __name__ == "main":
    import uvicorn

    uvicorn.run("main:app", host=settings.WS_HOST, port=settings.WS_PORT, reload=settings.DEBUG)