import asyncio
import json
import websockets
from src.auth.utils import decode_jwt
from src.config import settings
from src.db.dao import virtual_machine_dao, init_daos, VirtualMachineDAO, ConnectionHistoryDao, VMDiskDAO
from src.db.main import create_pool
from src.schemas import VMDiskCreate, VirtualMachineCreate
from src.websocket.exceptions import WebSocketNotConnectedError


class Client:
    def __init__(self, vm_id: int):
        self.vm_id = vm_id
        self.uri = f"ws://{settings.WS_HOST}:{settings.WS_PORT}/ws/{self.vm_id}"
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def close_connection(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def receive_json(self) -> dict:
        if self.websocket is None:
            raise WebSocketNotConnectedError
        data = await self.websocket.recv()
        return json.loads(data)

    async def send_data(self, data):
        if self.websocket is None:
            raise WebSocketNotConnectedError
        await self.websocket.send(json.dumps(data))

    async def authorize(self, token, public_key) -> bool:
        try:
            payload = decode_jwt(token, public_key)
            if 'vm_id' in payload and payload['vm_id'] == self.vm_id:
                return True
            else:
                return False
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    async def run(self):
        while True:
            try:
                data = await self.receive_json()
                data['public_key'] = settings.auth_jwt.public_key_path.read_text()
            except websockets.exceptions.ConnectionClosed:
                break

            if "error" in data:
                await self.close_connection()
                break

            data_type = data.get("type")
            if data_type is None:
                continue

            if data_type == "auth":
                is_authorized = await self.authorize(data['token'], data['public_key'])
                if is_authorized:
                    await self.send_data({"type": "success_auth"})
                else:
                    await self.send_data({"error": "authorization failed"})


async def test_socket():
    pool = await create_pool()
    virtual_machine_dao = VirtualMachineDAO(pool)
    connection_history_dao = ConnectionHistoryDao(pool)
    vm_disk_dao = VMDiskDAO(pool)

    vm1 = VirtualMachineCreate(
        name="VM1",
        ram=2048,
        cpu=2,
        description="Test VM 1",
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
        hard_disks=[
            VMDiskCreate(disk_id=3, disk_size=2000)
        ]
    )

    vm1_id = await virtual_machine_dao.create_vm(vm1)
    vm2_id = await virtual_machine_dao.create_vm(vm2)

    vm_client1 = Client(vm_id=vm1_id)
    vm_client2 = Client(vm_id=vm2_id)

    async def run_client(client):
        await client.connect()
        await client.send_data({"type": "init"})
        await client.run()

    await asyncio.gather(
        run_client(vm_client1),
        run_client(vm_client2)
    )


asyncio.run(test_socket())
