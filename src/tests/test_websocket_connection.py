import pytest
import asyncio
import websockets
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_websocket_connection(client):
    uri = "ws://localhost:8090/ws"

    async def websocket_test():
        async with websockets.connect(uri) as websocket:
            await websocket.send("test message")
            response = await websocket.recv()
            assert response == "Message received: test message"
            await websocket.close()

    await websocket_test()
