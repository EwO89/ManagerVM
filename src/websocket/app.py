from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth.utils import encode_jwt
from schemas import VirtualMachine, TokenInfo
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


def validate_auth_user():
    pass


@router.websocket.post("/token", response_model=TokenInfo)
def auth_vm_issue_jwt(
        vm: VirtualMachine = Depends(validate_auth_user),
):
    jwt_payload = {
        "sub": vm.id,
        "vm_name": vm.name,
        "vm_description": vm.description,
    }
    token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


