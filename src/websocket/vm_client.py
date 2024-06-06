import asyncio
import websockets
import json


class VMClient:
    def __init__(self, uri: str, vm_id: str):
        self.uri = uri
        self.vm_id = vm_id
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        await self.authorize()

    async def authorize(self):
        if self.websocket:
            auth_message = json.dumps({"action": "authorize", "vm_id": self.vm_id})
            await self.websocket.send(auth_message)
            response = await self.websocket.recv()
            print(f"Authorization response: {response}")

    async def send_message(self, message: str):
        if self.websocket:
            await self.websocket.send(message)
            response = await self.websocket.recv()
            print(f"Server response: {response}")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
