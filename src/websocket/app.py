from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.websocket import vm_server

router = APIRouter()


@router.websocket("/ws/{vm_id}")
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


@router.get("/vms")
async def list_virtual_machines():
    return vm_server.list_connected_clients()


@router.get("/vms/{vm_id}")
async def get_virtual_machine(vm_id: int):
    vm = vm_server.virtual_machines.get(vm_id)
    if vm:
        return vm.dict()
    return {"error": "Virtual machine not found"}


@router.get("/disks")
async def list_all_disks():
    return vm_server.list_all_disks()


@router.get("/connections")
async def list_all_connections():
    return vm_server.list_all_connections()
