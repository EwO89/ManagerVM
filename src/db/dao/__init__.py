from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao
from src.db.main import create_pool


class DAOs:
    def __init__(self, pool):
        self.virtual_machine_dao = VirtualMachineDAO(pool)
        self.connection_history_dao = ConnectionHistoryDao(pool)


async def get_daos():
    pool = await create_pool()
    return DAOs(pool)
