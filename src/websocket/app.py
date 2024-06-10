from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.websocket import vm_server

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, vm_id: int):
    await websocket.accept()
    try:
        vm = vm_server.virtual_machines.get(vm_id)
        if not vm:
            await websocket.send_json({"error": "Virtual machine not found"})
            await websocket.close()
            return

        await vm_server.handle_client(websocket, vm)
    except WebSocketDisconnect:
        vm_server.disconnect_client(vm_id)


