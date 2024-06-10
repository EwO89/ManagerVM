from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.websocket import websocket_server
from src.websocket.exceptions import Error

router = APIRouter()


@router.websocket("/ws/{vm_id}")
async def websocket_endpoint(websocket: WebSocket, vm_id: int):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            await websocket_server.handle_client(websocket, data, vm_id)
        except WebSocketDisconnect:
            websocket_server.disconnect_client(vm_id)
            break
        except Error as e:
            await websocket.close()
            print(e.error)
            break
        except Exception as e:
            await websocket.close()
            print(f"WebSocket unexpected error: {e}")
            break
