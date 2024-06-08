from datetime import datetime
from typing import List, Dict

from src.config import settings
import asyncpg


class ConnectionHistoryDao:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(settings.POSTGRES_URL)

    async def create(self, vm_id: int):
        await self.create_pool()
        async with self.pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO ws_connection_history (vm_id, connected_at)
                VALUES ($1, $2)
            ''', vm_id, datetime.utcnow())

    async def get_all_distinct(self) -> List[Dict]:
        await self.create_pool()
        async with self.pool.acquire() as connection:
            rows = await connection.fetch('''
                SELECT DISTINCT vm_id, MIN(connected_at) as first_connected_at
                FROM ws_connection_history
                GROUP BY vm_id
                ORDER BY first_connected_at
            ''')
            return [dict(row) for row in rows]

    async def get_all(self) -> List[Dict]:
        await self.create_pool()
        async with self.pool.acquire() as connection:
            rows = await connection.fetch('''
                SELECT vm_id, connected_at
                FROM ws_connection_history
                ORDER BY connected_at
            ''')
            return [dict(row) for row in rows]
