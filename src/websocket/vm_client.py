import asyncio
import json

import jwt
import websockets

from src.auth.utils import decode_jwt
from src.config import settings
from src.db.dao import virtual_machine_dao, init_daos, VirtualMachineDAO, ConnectionHistoryDao, VMDiskDAO
from src.db.main import create_pool
from src.schemas import VMDiskCreate, VirtualMachineCreate
from src.websocket.exceptions import WebSocketNotConnectedError
from src.websocket import websocket_server


class Client:
    def __init__(self, vm_id: int):
        self.vm_id = vm_id
        self.uri = f"ws://{settings.WS_HOST}:{settings.WS_PORT}/ws/{self.vm_id}"
        self.websocket = None

    async def connect(self):
        print(f"Connecting to {self.uri}")
        self.websocket = await websockets.connect(self.uri)

        print('good')

    async def close_connection(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def receive_json(self) -> dict:
        if self.websocket is None:
            raise WebSocketNotConnectedError
        print(f"{self.websocket}")
        data = await self.websocket.recv()
        print(data)
        print('kek')
        return json.loads(data)

    async def send_data(self, data):
        if self.websocket is None:
            raise WebSocketNotConnectedError
        await self.websocket.send(json.dumps(data))

    async def authorize(self, token, public_key) -> bool:
        print('real?')
        print(public_key)
        try:
            payload = decode_jwt(token, public_key)
            print(payload)
            print(self.vm_id)
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
                print('??????ЮЮ')
                data = await self.receive_json()
                data['public_key'] = settings.auth_jwt.public_key_path.read_text()
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by the server")
                break
            print("Received data: ", data)
            print('seriosli?')
            if "error" in data:
                print("Error occured: ", data["error"])
                await self.close_connection()
                break

            data_type = data.get("type")
            if data_type is None:
                continue

            if data_type == "auth":
                is_authorized = await self.authorize(data['token'], data['public_key'])
                if is_authorized:
                    print("Authorization success")
                    await self.send_data({"type": "success_auth"})
                else:
                    print("Authorization failed")
                    await self.send_data({"error": "authorization failed"})
            data = await websocket_server.authorized_connections
            return data


async def test_socket():
    pool = await create_pool()
    virtual_machine_dao = VirtualMachineDAO(pool)
    connection_history_dao = ConnectionHistoryDao(pool)
    vm_disk_dao = VMDiskDAO(pool)
    vm_client = Client(vm_id=1)
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
    print(f"Created VMs with IDs: {vm1_id}, {vm2_id}")
    await vm_client.connect()
    await vm_client.send_data({"type": "init"})
    await vm_client.run()


asyncio.run(test_socket())
