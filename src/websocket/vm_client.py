import asyncio
import json

import jwt
import websockets

from src.auth.utils import decode_jwt
from src.config import settings
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
            if 'id' in payload and payload['id'] == self.vm_id:
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
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed by the server")
                break

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


async def test_socket():
    vm_client = Client(vm_id=1)

    await vm_client.connect()
    await vm_client.send_data({"type": "init"})
    await vm_client.run()


asyncio.run(test_socket())
