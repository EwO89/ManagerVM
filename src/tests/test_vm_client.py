import pytest
import asyncio
from fastapi import FastAPI, WebSocketDisconnect
from fastapi.testclient import TestClient
from src.websocket.vm_client import VMClient
from src.websocket import websocket_server
from src.websocket.app import router as websocket_router
from src.config import settings


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(websocket_router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.mark.asyncio
async def test_vm_client(client):
    server_uri = f"ws://{settings.WS_HOST}:{settings.WS_PORT}/ws/vm123"

    async def run_server():
        async with client.websocket_connect(server_uri) as websocket:
            await websocket_server.register(websocket, "vm123")
            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket_server.send_message(f"Message received: {data}")
            except WebSocketDisconnect:
                await websocket_server.disconnect(websocket)
                await websocket_server.send_message("A client disconnected")

    server_task = asyncio.create_task(run_server())

    vm_client = VMClient(server_uri, "vm123")

    await vm_client.connect()
    await vm_client.send_message("Hello from VMClient")
    await vm_client.close()

    server_task.cancel()

    assert len(websocket_server.active_connections) == 0
    assert any(conn["vm_id"] == "vm123" for conn in websocket_server.all_connections_list)
