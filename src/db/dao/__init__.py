from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao
from src.db.main import create_pool

virtual_machine_dao = None
connection_history_dao = None

async def init_daos():
    global virtual_machine_dao, connection_history_dao
    pool = await create_pool()
    virtual_machine_dao = VirtualMachineDAO(pool)
    connection_history_dao = ConnectionHistoryDao(pool)
