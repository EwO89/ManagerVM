from src.db.dao.virtual_machine import VirtualMachineDAO
from src.db.dao.connection_history import ConnectionHistoryDao
from src.db.dao.vm_disk import VMDiskDAO
from src.db.main import create_pool

virtual_machine_dao: VirtualMachineDAO | None = None
connection_history_dao: ConnectionHistoryDao | None = None
vm_disk_dao: VMDiskDAO | None = None


async def init_daos():
    global virtual_machine_dao, connection_history_dao, vm_disk_dao
    pool = await create_pool()
    virtual_machine_dao = VirtualMachineDAO(pool)
    connection_history_dao = ConnectionHistoryDao(pool)
    vm_disk_dao = VMDiskDAO(pool)
    print("DAO initialized:", virtual_machine_dao, connection_history_dao, vm_disk_dao)
