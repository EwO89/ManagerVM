import websockets

from src.auth.utils import encode_jwt
from src.config import settings
from src.db.dao import virtual_machine_dao, connection_history_dao
from src.schemas import VirtualMachine, VirtualMachineCreate, VMDiskCreate
from fastapi import WebSocket


class WebsocketServer:
    def __init__(self):
        self.virtual_machines = {}
        self.virtual_machines_active_connections = []
        self.authorized_clients = []

    async def request_authorization(self, websocket, vm: VirtualMachine):
        try:
            token = encode_jwt({"vm_id": vm.vm_id})
            await websocket.send(token)
            await websocket.send(settings.auth_jwt.public_key_path.read_text())

            response = await websocket.recv()
            if response == "authenticated":
                print(f"Authenticated with {vm.vm_id}")
                self.virtual_machines_active_connections.append(vm)
                self.authorized_clients.append(vm)
                await self.handle_client(websocket, vm)
            else:
                print(f"Failed to authenticate with {vm.vm_id}")
                await websocket.send_json({"error": "Failed to authenticate"})
                await websocket.close()
        except Exception as e:
            print(f"Authorization error with {vm.vm_id}: {e}")
            await websocket.send_json({"error": "Authorization error"})
            await websocket.close()

    async def handle_client(self, websocket: WebSocket, vm: VirtualMachine):
        try:
            while True:
                message = await websocket.receive_json()
                print(f"Received message from {vm.vm_id}: {message}")
                if message["type"] == "init":
                    pass
                elif message["type"] == "data":
                    pass
                else:
                    pass
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {vm.vm_id}")
            await connection_history_dao.close_connection(vm.vm_id)
            self.virtual_machines_active_connections.remove(vm)

    async def list_connected_clients(self):
        vms = await virtual_machine_dao.list_vms()
        return [vm.dict() for vm in vms if vm.is_connected]

    async def list_authorized_clients(self):
        return [vm.dict() for vm in self.authorized_clients]

    async def list_all_disks(self):
        vms = await virtual_machine_dao.list_vms()
        disks = []
        for vm in vms:
            for disk in vm.hard_disks:
                disk_info = disk.dict()
                disk_info['vm_name'] = vm.name
                disks.append(disk_info)
        return disks

    async def list_all_connections(self):
        return await connection_history_dao.get_all()

    async def disconnect_client(self, vm_id: int):
        vm = await virtual_machine_dao.get_vm(vm_id)
        if vm and vm.is_authenticated:
            await self.close_connection(vm)

    async def close_connection(self, vm: VirtualMachine):
        try:
            await vm.websocket.close()
        except Exception as e:
            print(f"Error closing connection for {vm.vm_id}: {e}")
        finally:
            await connection_history_dao.close_connection(vm.vm_id)

    async def update_vm(self, vm_id: int, ram: int = None, cpu: int = None, description: str = None):
        vm = await virtual_machine_dao.get_vm(vm_id)
        if vm:
            updated_vm = VirtualMachineCreate(
                name=vm.name,
                ram=ram if ram is not None else vm.ram,
                cpu=cpu if cpu is not None else vm.cpu,
                description=description if description is not None else vm.description,
                uri=vm.uri,
                hard_disks=[VMDiskCreate(disk_id=disk.disk_id, disk_size=disk.disk_size) for disk in vm.hard_disks]
            )
            await virtual_machine_dao.update_vm(vm_id, updated_vm)
            print(f"Updated VM {vm_id}: {updated_vm.dict()}")


vm_server = WebsocketServer()
