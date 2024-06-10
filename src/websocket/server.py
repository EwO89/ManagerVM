import jwt
import websockets

from src.auth.utils import encode_jwt, decode_jwt
from src.config import settings
from src.db.dao import virtual_machine_dao, connection_history_dao
from src.schemas import VirtualMachine, VirtualMachineCreate, VMDiskCreate
from fastapi import WebSocket


class WebsocketServer:
    def __init__(self):
        self.virtual_machines_info = {}
        self.virtual_machines_active_connections = {}
        self.authorized_clients = {}

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
        self.virtual_machines_info[websocket] = vm
        try:
            while True:
                message = await websocket.receive_json()
                print(f"Received message from {vm.vm_id}: {message}")
                # server -> payload {type:'auth'}. 1)
                if message["type"] == "init":
                    await self.request_authorization(websocket, vm)
                elif message["type"] == "auth":
                    token = message.get("token")
                    public_key = settings.auth_jwt.public_key_path.read_text()
                    try:
                        payload = decode_jwt(token, public_key)
                        if 'vm_id' in payload and payload['vm_id'] == vm.vm_id:
                            print(f"Authenticated with {vm.vm_id}")
                            self.virtual_machines_active_connections[vm.vm_id] = websocket
                            self.authorized_clients[vm.vm_id] = websocket
                            await websocket.send_json({"type": "success_auth"})
                        else:
                            await websocket.send_json({"error": "Failed to authenticate"})
                            await websocket.close()
                    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                        await websocket.send_json({"error": "Invalid token"})
                        await websocket.close()
                elif message["type"] == "data":
                    print(f"Data from {vm.vm_id}: {message['data']}")
                else:
                    print(f"Unknown message type from {vm.vm_id}: {message['type']}")

    '''async def handle_client(self, websocket: WebSocket, vm: VirtualMachine):
        try:
            while True:
                message = await websocket.receive_json()
                print(f"Received message from {vm.vm_id}: {message}")
                if message["type"] == "init":
                    await self.request_authorization(websocket, vm)
                elif message["type"] == "data":
                    pass
                else:
                    pass
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {vm.vm_id}")
            await connection_history_dao.close_connection(vm.vm_id)
            self.virtual_machines_active_connections.remove(vm)'''

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


async def close_connection(self, websocket: WebSocket, vm_id: int):
    try:
        await websocket.close()
    except Exception as e:
        print(f"Error closing connection for {vm_id}: {e}")
    finally:
        await connection_history_dao.close_connection(vm_id)
        if websocket in self.virtual_machines_info:
            del self.virtual_machines_info[websocket]
        if vm_id in self.virtual_machines_active_connections:
            del self.virtual_machines_active_connections[vm_id]
        if vm_id in self.authorized_clients:
            del self.authorized_clients[vm_id]