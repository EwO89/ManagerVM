import asyncpg
from src.config import settings


async def create_pool():
    return await asyncpg.create_pool(settings.POSTGRES_URL)


async def init_db():
    pool = await create_pool()

    async with pool.acquire() as connection:
        result = await connection.fetch("SELECT 'hello' AS greeting;")
        print(result)
