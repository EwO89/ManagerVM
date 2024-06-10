from fastapi import FastAPI
from src.config import settings
from src.db.dao import init_daos
from src.websocket.app import router as websocket_router
from src.db.main import create_tables

app = FastAPI(
    title="ManagerVM",
    version="1.0.0",
    description="Manager VM service",
)


@app.on_event("startup")
async def startup_event():
    await create_tables()
    await init_daos()

app.include_router(websocket_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.WS_HOST, port=settings.WS_PORT, reload=settings.DEBUG)
