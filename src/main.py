from fastapi import FastAPI
from src.websocket.app import router as websocket_router

app = FastAPI(
    title="ManagerVM",
    version="1.0.0",
    description="Manager VM service",
)
app.include_router(websocket_router)
