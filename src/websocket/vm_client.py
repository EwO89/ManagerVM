import asyncio
import websockets
from src.auth.utils import decode_jwt
import jwt


async def handle_connection(websocket, path):
    try:
        token = await websocket.recv()
        public_key = await websocket.recv()

        vm_id = None
        try:
            payload = decode_jwt(token, public_key=public_key)
            vm_id = payload["vm_id"]
        except jwt.ExpiredSignatureError:
            await websocket.send("unauthorized")
        except jwt.InvalidTokenError:
            await websocket.send("unauthorized")

        if vm_id:
            await websocket.send("authenticated")
            print(f"Authenticated with token: {token}")

            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")
                # Обработка сообщений от сервера
        else:
            await websocket.send("unauthorized")
            print("Failed to authenticate")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")


async def run_client(host, port):
    server = await websockets.serve(handle_connection, host, port)
    async with server:
        await asyncio.Future()
