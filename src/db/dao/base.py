import asyncpg


class BaseDAO:
    def __init__(self, pool: asyncpg.pool.Pool):
        self.pool = pool
