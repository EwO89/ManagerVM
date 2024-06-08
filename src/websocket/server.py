import asyncio
import websockets
from src.auth.utils import encode_jwt
from src.config import settings
from src.schemas import VirtualMachine, WSConnectionHistoryCreate, VirtualMachineCreate, VMDiskCreate
from datetime import datetime
from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao


class WebsocketServer:
    def __init__(self, virtual_machine_dao: VirtualMachineDAO, connection_history_dao: ConnectionHistoryDao):
        self.virtual_machine = virtual_machine_dao
        self.connection_history = connection_history_dao

    async def connect_to_client(self, vm: VirtualMachine):
        try:
            async with websockets.connect(vm.uri) as websocket:
                print(f"Connected to {vm.vm_id}")
                await self.connection_history.create(vm.vm_id)

                await self.request_authorization(websocket, vm)
        except Exception as e:
            print(f"Failed to connect to {vm.uri}: {e}")

    async def request_authorization(self, websocket, vm: VirtualMachine):
        try:
            token = encode_jwt({"vm_id": vm.vm_id})
            await websocket.send(token)
            await websocket.send(settings.auth_jwt.public_key_path.read_text())

            response = await websocket.recv()
            if response == "authenticated":
                print(f"Authenticated with {vm.vm_id}")
                await self.handle_client(websocket, vm)
            else:
                print(f"Failed to authenticate with {vm.vm_id}")
        except Exception as e:
            print(f"Authorization error with {vm.vm_id}: {e}")

    async def handle_client(self, websocket, vm: VirtualMachine):
        try:
            while True:
                message = await websocket.recv()
                print(f"Received message from {vm.vm_id}: {message}")

        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {vm.vm_id}")
            await self.connection_history.close_connection(vm.vm_id)

    async def list_connected_clients(self):
        vms = await self.virtual_machine.list_vms()
        return [vm.dict() for vm in vms if vm.is_connected]

    async def list_authorized_clients(self):
        vms = await self.virtual_machine.list_vms()
        return [vm.dict() for vm in vms if vm.is_authenticated]

    async def list_all_disks(self):
        vms = await self.virtual_machine.list_vms()
        disks = []
        for vm in vms:
            for disk in vm.hard_disks:
                disk_info = disk.dict()
                disk_info['vm_name'] = vm.name
                disks.append(disk_info)
        return disks

    async def list_all_connections(self):
        return await self.connection_history.get_all()

    async def disconnect_client(self, vm_id: int):
        vm = await self.virtual_machine.get_vm(vm_id)
        if vm and vm.is_authenticated:
            await self.close_connection(vm)

    async def close_connection(self, vm: VirtualMachine):
        try:
            await vm.websocket.close()
        except Exception as e:
            print(f"Error closing connection for {vm.vm_id}: {e}")
        finally:
            await self.connection_history.close_connection(vm.vm_id)

    async def update_vm(self, vm_id: int, ram: int = None, cpu: int = None, description: str = None):
        vm = await self.virtual_machine.get_vm(vm_id)
        if vm:
            updated_vm = VirtualMachineCreate(
                name=vm.name,
                ram=ram if ram is not None else vm.ram,
                cpu=cpu if cpu is not None else vm.cpu,
                description=description if description is not None else vm.description,
                uri=vm.uri,
                hard_disks=[VMDiskCreate(disk_id=disk.disk_id, disk_size=disk.disk_size) for disk in vm.hard_disks]
            )
            await self.virtual_machine.update_vm(vm_id, updated_vm)
            print(f"Updated VM {vm_id}: {updated_vm.dict()}")

    async def run(self):
        vm1 = VirtualMachineCreate(
            name="VM1",
            ram=2048,
            cpu=2,
            description="Test VM 1",
            uri="ws://localhost:8765",
            hard_disks=[
                VMDiskCreate(disk_id=1, disk_size=500),
                VMDiskCreate(disk_id=2, disk_size=1000)
            ]
        )

        vm2 = VirtualMachineCreate(
            name="VM2",
            ram=4096,
            cpu=4,
            description="Test VM 2",
            uri="ws://localhost:8766",
            hard_disks=[
                VMDiskCreate(disk_id=3, disk_size=2000)
            ]
        )

        vm1_id = await self.virtual_machine.create_vm(vm1)
        vm2_id = await self.virtual_machine.create_vm(vm2)

        vms = [await self.virtual_machine.get_vm(vm1_id), await self.virtual_machine.get_vm(vm2_id)]
        await asyncio.gather(*[self.connect_to_client(vm) for vm in vms if vm is not None])
