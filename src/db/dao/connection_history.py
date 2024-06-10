from datetime import datetime
from typing import List
import asyncpg
from src.db.dao.base import BaseDAO
from src.schemas import WSConnectionHistory

class ConnectionHistoryDao(BaseDAO):
    def __init__(self, pool: asyncpg.pool.Pool):
        self.table_name = 'ws_connection_history'
        super().__init__(pool)

    async def create(self, vm_id: int):
        async with self.pool.acquire() as connection:
            await connection.execute(f'''
                INSERT INTO {self.table_name} (vm_id, connected_at)
                VALUES ($1, $2)
            ''', vm_id, datetime.utcnow())

    async def get_all_distinct(self) -> List[WSConnectionHistory]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(f'''
                SELECT DISTINCT vm_id, MIN(connected_at) as first_connected_at
                FROM {self.table_name}
                GROUP BY vm_id
                ORDER BY first_connected_at
            ''')
            return [WSConnectionHistory(vm_id=row['vm_id'], connected_at=row['first_connected_at']) for row in rows]

    async def get_all(self) -> List[WSConnectionHistory]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(f'''
                SELECT id, vm_id, connected_at, disconnected_at
                FROM {self.table_name}
                ORDER BY connected_at
            ''')
            return [WSConnectionHistory(id=row['id'], vm_id=row['vm_id'], connected_at=row['connected_at'],
                                        disconnected_at=row['disconnected_at']) for row in rows]

    async def close_connection(self, vm_id: int):
        async with self.pool.acquire() as connection:
            await connection.execute(f'''
                UPDATE {self.table_name}
                SET disconnected_at = $1
                WHERE vm_id = $2 AND disconnected_at IS NULL
            ''', datetime.utcnow(), vm_id)
