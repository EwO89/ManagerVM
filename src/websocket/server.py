from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from datetime import datetime
from src.db.main import create_pool
from auth.utils import decode_jwt


class WebSocketServer:
    def __init__(self):
        self.active_connections: List[Dict] = []
        self.all_connections: List[Dict] = []

    async def register(self, websocket: WebSocket, vm_id: str):
        await websocket.accept()
        vm_data = await self.get_vm_data(vm_id)
        connection_info = {
            "vm_id": vm_data["vm_id"],
            "name": vm_data["name"],
            "ram": vm_data["ram"],
            "cpu": vm_data["cpu"],
            "websocket": websocket,
            "connected_at": datetime.utcnow()
        }
        self.active_connections.append(connection_info)
        self.all_connections.append(connection_info)
        await self.save_connection_info(vm_data["vm_id"])

    async def disconnect(self, websocket: WebSocket):
        for conn in self.active_connections:
            if conn["websocket"] == websocket:
                conn["disconnected_at"] = datetime.utcnow()
                self.active_connections.remove(conn)
                break

    async def get_vm_data(self, vm_id: str):
        pool = await create_pool()
        async with pool.acquire() as connection:
            vm_data = await connection.fetchrow('''
                SELECT vm_id, name, ram, cpu
                FROM virtual_machine
                WHERE vm_id = $1
            ''', vm_id)
            if vm_data is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="VM not found")
            return dict(vm_data)

    async def get_all_vms(self):
        pool = await create_pool()
        async with pool.acquire() as connection:
            vms = await connection.fetch('''
                SELECT vm_id, name, ram, cpu
                FROM virtual_machine
            ''')
            return [dict(vm) for vm in vms]

    async def save_connection_info(self, vm_id: int):
        pool = await create_pool()
        async with pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO ws_connection_history (vm_id, connected_at)
                VALUES ($1, $2)
            ''', vm_id, datetime.utcnow())

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            await connection["websocket"].send_text(message)

    async def authorize(self, websocket: WebSocket):
        token = websocket.headers.get("Authorization")
        if token is None or not token.startswith("Bearer "):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

        token = token.split("Bearer ")[1]
        try:
            payload = decode_jwt(token)
        except HTTPException:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return payload

    async def get_active_vms(self, websocket: WebSocket):
        active_vms = [
            {k: v for k, v in conn.items() if k in ["vm_id", "name", "ram", "cpu"]}
            for conn in self.active_connections
            if conn.get("disconnected_at") is None
        ]
        await self.send_message(websocket, {"active_vms": active_vms})

    async def get_authorized_vms(self, websocket: WebSocket):
        authorized_vms = [
            {k: v for k, v in conn.items() if k in ["vm_id", "name", "ram", "cpu"]}
            for conn in self.active_connections
            if conn.get("disconnected_at") is None
        ]
        await self.send_message(websocket, {"authorized_vms": authorized_vms})

    async def get_all_vms_info(self, websocket: WebSocket):
        all_vms = await self.get_all_vms()
        await self.send_message(websocket, {"all_vms": all_vms})

    async def get_all_connected_vms(self, websocket: WebSocket):
        all_connected_vms = [
            {k: v for k, v in conn.items() if k in ["vm_id", "name", "ram", "cpu", "connected_at"]}
            for conn in self.all_connections
        ]
        await self.send_message(websocket, {"all_connected_vms": all_connected_vms})
