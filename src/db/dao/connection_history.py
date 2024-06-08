from datetime import datetime
from typing import List, Dict

import asyncpg

from src.config import settings


class BaseDao:
    def __init__(self, pool):
        self.pool = pool


class ConnectionHistoryDao:
    def __init__(self):
        self.table_name = 'ws_connection_history'

    async def create(self, vm_id: int):
        async with self.pool.acquire() as connection:
            await connection.execute(f'''
                INSERT INTO {self.table_name} (vm_id, connected_at)
                VALUES ($1, $2)
            ''', vm_id, datetime.utcnow())

    async def get_all_distinct(self) -> List[Dict]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(f'''
                SELECT DISTINCT vm_id, MIN(connected_at) as first_connected_at
                FROM {self.table_name}
                GROUP BY vm_id
                ORDER BY first_connected_at
            ''')
            return [dict(row) for row in rows]

    async def get_all(self) -> List[Dict]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(f'''
                SELECT vm_id, connected_at
                FROM {self.table_name}
                ORDER BY connected_at
            ''')
            return [dict(row) for row in rows]
