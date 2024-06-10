from src.auth.utils import encode_jwt, decode_jwt
from src.config import settings
from src.db.dao import virtual_machine_dao, connection_history_dao
from src.schemas import VirtualMachineModel, VirtualMachineCreate, VMDiskCreate
from fastapi import WebSocket
import jwt


class WebsocketServer:
    def __init__(self):
        self.virtual_machines_info = {}
        self.virtual_machines_active_connections = {}
        self.authorized_clients = {}

    async def request_authorization(self, websocket: WebSocket, vm: VirtualMachineModel):
        pass

    async def handle_client(self, websocket: WebSocket, vm: VirtualMachineModel):
        pass

    async def list_connected_clients(self):
        return list(self.virtual_machines_info.values())

    async def list_authorized_clients(self):
        return list(self.authorized_clients.values())

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
        if vm_id in self.virtual_machines_active_connections:
            websocket = self.virtual_machines_active_connections[vm_id]
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
