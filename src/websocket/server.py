from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncpg
from src.config import settings

class WebSocketServer:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.all_connections: List[Dict] = []

    async def create_pool(self):
        return await asyncpg.create_pool(dsn=settings.POSTGRES_URL)

    async def register(self, websocket: WebSocket, vm_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        connection_info = {
            "vm_id": vm_id,
            "websocket": websocket,
            "connected_at": datetime.utcnow()
        }
        self.all_connections.append(connection_info)
        await self.save_connection_info(vm_id)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        for conn in self.all_connections:
            if conn["websocket"] == websocket:
                conn["disconnected_at"] = datetime.utcnow()
                break

    @property
    def active_connections_list(self):
        return [{"vm_id": conn["vm_id"], "connected_at": conn["connected_at"]} for conn in self.all_connections if conn.get("disconnected_at") is None]

    @property
    def authorized_connections_list(self):
        return self.active_connections_list

    @property
    def all_connections_list(self):
        return self.all_connections

    async def save_connection_info(self, vm_id: str):
        pool = await self.create_pool()
        async with pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO ws_connection_history (vm_id, connected_at)
                VALUES ($1, $2)
            ''', vm_id, datetime.utcnow())

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
