from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao
from src.db.main import create_pool
import asyncio


async def init_daos():
    pool = await create_pool()
    virtual_machine_dao = VirtualMachineDAO(pool)
    connection_history_dao = ConnectionHistoryDao(pool)
    return virtual_machine_dao, connection_history_dao


virtual_machine_dao, connection_history_dao = asyncio.run(init_daos())
