from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.websocket import vm_server
from src.db.dao import virtual_machine_dao

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        vm_id = await websocket.recv()
        vm = await virtual_machine_dao.get_vm(vm_id)
        if not vm:
            await websocket.send_json({"error": "Virtual machine not found"})
            await websocket.close()
            return

        if vm.vm_id not in vm_server.virtual_machines:
            vm_server.virtual_machines[vm.vm_id] = vm

        if vm in vm_server.authorized_clients:
            print(f"Client {vm.vm_id} is already authenticated")
            vm_server.virtual_machines_active_connections.append(vm)
            await vm_server.handle_client(websocket, vm)
        else:
            await vm_server.request_authorization(websocket, vm)

    except WebSocketDisconnect:
        await vm_server.disconnect_client(vm_id)
