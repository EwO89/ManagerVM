from fastapi import WebSocket
import asyncpg
from src.auth.utils import encode_jwt
from src.config import settings
from src.db.dao import connection_history_dao
from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao
from src.db.dao.vm_disk import VMDiskDAO
from src.schemas import VirtualMachineCreate, VMDiskCreate, VirtualMachineUpdate
from src.websocket.exceptions import ServerError, UnknownType


class WebsocketServer:
    data_types = ["init", "success_auth", "error", "data"]

    def __init__(self):
        self.vm_info = {}
        self.active_connections = {}
        self.authorized_connections = {}
        self.pool = None

    async def init_pool(self):
        self.pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)

    async def authorize(self, websocket: WebSocket, vm: VirtualMachineCreate):
        token = encode_jwt({"vm_id": vm.vm_id})
        data = {"type": "auth", "token": token, "public_key": settings.auth_jwt.public_key_path.name}
        await websocket.send_json(data)

    async def _is_authorized(self, vm_id: int):
        return vm_id in self.authorized_connections

    async def handle_client(self, websocket: WebSocket, data: dict, vm_id: int):
        if self.pool is None:
            await self.init_pool()

        virtual_machine_dao = VirtualMachineDAO(self.pool)

        vm = await virtual_machine_dao.get_vm(vm_id)
        if vm is None:
            print(f"Virtual machine with vm_id {vm_id} not found")
            return

        print(f"Received message from {vm.vm_id}: {data}")

        data_type = data.get("type")

        if data_type not in self.data_types:
            raise UnknownType

        if data_type == "init":
            await self._handle_init(websocket, vm)
        elif data_type == "success_auth":
            await self._handle_success_auth(websocket, vm)
        elif data_type == "data":
            await self._handle_update(vm.vm_id, data['data'])
        else:
            await self._handle_error(vm.vm_id, data['error'])
            print(f"Error from {vm.vm_id}: {data['error']}")
            await self.disconnect_client(vm.vm_id)
            raise ServerError(data['error'])

    async def _handle_init(self, websocket: WebSocket, vm: VirtualMachineCreate):
        if self._is_authorized(vm.vm_id):
            print("Already authorized, client can send data")
        else:
            self.active_connections[vm.vm_id] = websocket
            self.vm_info[vm.vm_id] = vm
            await self.authorize(websocket, vm)

    async def _handle_success_auth(self, websocket: WebSocket, vm: VirtualMachineCreate):
        self.authorized_connections[vm.vm_id] = websocket
        print(f"Authorized {vm.vm_id}")

    async def _handle_update(self, vm_id: int, data: dict):
        update_data = VirtualMachineUpdate(**data)
        await self.update_vm(vm_id, update_data)

    async def _handle_error(self, vm_id: int, error: str):
        print(f"Error from {vm_id}: {error}")
        await self.disconnect_client(vm_id)
        raise ServerError(error)

    async def list_active_connections(self):
        return [self.vm_info[vm_id] for vm_id in self.active_connections]

    async def list_authorized_connections(self):
        return [self.vm_info[vm_id] for vm_id in self.authorized_connections]

    async def list_all_disks(self):
        if self.pool is None:
            await self.init_pool()

        vm_disk_dao = VMDiskDAO(self.pool)
        return await vm_disk_dao.get_all()

    async def list_all_connections(self):
        if self.pool is None:
            await self.init_pool()

        connection_history_dao = ConnectionHistoryDao(self.pool)
        return await connection_history_dao.get_all_distinct()

    async def disconnect_client(self, vm_id: int):
        if vm_id in self.active_connections:
            websocket = self.active_connections[vm_id]
            await websocket.close()
            await connection_history_dao.close_connection(vm_id)
            if websocket in self.vm_info:
                del self.vm_info[websocket]
            if vm_id in self.active_connections:
                del self.active_connections[vm_id]
            if vm_id in self.authorized_connections:
                del self.authorized_connections[vm_id]

    async def update_vm(self, vm_id: int, vm_data: VirtualMachineUpdate):
        if self.pool is None:
            await self.init_pool()

        virtual_machine_dao = VirtualMachineDAO(self.pool)
        vm = await virtual_machine_dao.get_vm(vm_id)
        if vm:
            updated_vm = VirtualMachineCreate(
                name=vm.name,
                ram=vm_data.ram if vm_data.ram is not None else vm.ram,
                cpu=vm_data.cpu if vm_data.cpu is not None else vm.cpu,
                description=vm_data.description if vm_data.description is not None else vm.description,
                hard_disks=[VMDiskCreate(disk_id=disk.disk_id, disk_size=disk.disk_size) for disk in
                            vm.hard_disks] if vm_data.hard_disks is not None else vm.hard_disks
            )
            await virtual_machine_dao.update_vm(vm_id, updated_vm)
            print(f"Updated VM {vm_id}: {updated_vm.dict()}")



