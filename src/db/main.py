import asyncpg
from src.config import settings
import os


async def create_pool():
    return await asyncpg.create_pool(settings.POSTGRES_URL)


async def read_sql_script(file_path):
    with open(file_path, 'r') as file:
        sql_script = file.read()
    return sql_script


async def init_db():
    pool = await create_pool()

    async with pool.acquire() as connection:
        result = await connection.fetch("SELECT 'hello' AS greeting;")
        print(result)


async def create_tables():
    pool = await create_pool()
    script_path = os.path.join(os.path.dirname(__file__), 'create_tables.sql')
    sql_script = await read_sql_script(script_path)

    async with pool.acquire() as connection:
        await connection.execute(sql_script)

    executed_script_path = os.path.join(os.path.dirname(__file__), 'executed_tables.sql')
    with open(executed_script_path, 'w') as file:
        file.write(sql_script)

    await pool.close()
