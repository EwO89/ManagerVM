import asyncpg
from pathlib import Path
from src.config import settings


async def create_pool():
    return await asyncpg.create_pool(settings.POSTGRES_URL)


async def read_sql_script(file_path: Path):
    with open(file_path, 'r') as file:
        sql_script = file.read()
    return sql_script


async def create_tables():
    pool = await create_pool()
    script_path = settings.BASE_DIR / 'src' / 'db' / 'sql' / 'create_tables.sql'
    sql_script = await read_sql_script(script_path)

    async with pool.acquire() as connection:
        await connection.execute(sql_script)

    executed_script_path = settings.BASE_DIR / 'src' / 'db' / 'sq' / 'executed_tables.sql'
    with open(executed_script_path, 'w') as file:
        file.write(sql_script)

    await pool.close()
