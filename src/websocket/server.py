import asyncio
import websockets
from auth.utils import encode_jwt, decode_jwt
from src.config import settings
from schemas import VirtualMachineCreate, VirtualMachine, VMDiskCreate, VMDisk, WSConnectionHistoryCreate, WSConnectionHistory, TokenInfo
from datetime import datetime

class VirtualMachineServer:
    def __init__(self):
        self.virtual_machines = {}

    async def connect_to_client(self, vm: VirtualMachine):
        try:
            async with websockets.connect(vm.uri) as websocket:
                # Этап подключения
                print(f"Connected to {vm.vm_id}")
                vm.is_connected = True

                # Отправляем запрос на авторизацию
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
                vm.is_authenticated = True
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
                # Обработка сообщений от клиента
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {vm.vm_id}")
            vm.is_connected = False
            vm.is_authenticated = False

    def list_connected_clients(self):
        return [vm.dict() for vm in self.virtual_machines.values() if vm.is_connected]

    def list_authorized_clients(self):
        return [vm.dict() for vm in self.virtual_machines.values() if vm.is_authenticated]

    def list_all_disks(self):
        disks = []
        for vm in self.virtual_machines.values():
            for disk in vm.hard_disks:
                disk_info = disk.dict()
                disk_info['vm_name'] = vm.name
                disks.append(disk_info)
        return disks

    async def run(self):
        # Создание примеров виртуальных машин
        vm1 = VirtualMachine(
            vm_id=1,
            name="VM1",
            ram=2048,
            cpu=2,
            description="Test VM 1",
            uri="ws://localhost:8765",
            created_at=datetime.utcnow(),
            hard_disks=[
                VMDisk(disk_id=1, vm_id=1, disk_size=500),
                VMDisk(disk_id=2, vm_id=1, disk_size=1000)
            ]
        )

        vm2 = VirtualMachine(
            vm_id=2,
            name="VM2",
            ram=4096,
            cpu=4,
            description="Test VM 2",
            uri="ws://localhost:8766",
            created_at=datetime.utcnow(),
            hard_disks=[
                VMDisk(disk_id=3, vm_id=2, disk_size=2000)
            ]
        )

        self.virtual_machines = {
            vm1.vm_id: vm1,
            vm2.vm_id: vm2
        }

        await asyncio.gather(*[self.connect_to_client(vm) for vm in self.virtual_machines.values()])

if __name__ == "__main__":
    server = VirtualMachineServer()
    asyncio.run(server.run())
