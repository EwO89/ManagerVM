from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from . import websocket_server

router = APIRouter()


@router.websocket("/ws/{vm_id}")
async def websocket_endpoint(websocket: WebSocket, vm_id: str):
    await websocket_server.register(websocket, vm_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_server.send_message(f"Message received: {data}")
    except WebSocketDisconnect:
        await websocket_server.disconnect(websocket)
        await websocket_server.send_message("A client disconnected")
