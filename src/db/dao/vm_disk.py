
from typing import List

from src.db.dao.base import BaseDAO
from src.schemas import VMDiskModel, VirtualMachineModel


class VMDiskDAO(BaseDAO):
    def __init__(self, pool):
        self.table_name = "vm_disk"
        super().__init__(pool)

    async def get_all(self) -> List[VMDiskModel]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(f'''
                SELECT disk_id, vm_id, disk_size, vm_id, name, ram, cpu, description, uri, created_at
                FROM {self.table_name}
                JOIN virtual_machine ON vm_disk.vm_id = virtual_machine.vm_id
            ''')
            return [
                VMDiskModel(
                    disk_id=row['disk_id'],
                    vm=VirtualMachineModel(
                        vm_id=row['vm_id'],
                        name=row['name'],
                        ram=row['ram'],
                        cpu=row['cpu'],
                        description=row['description'],
                        uri=row['uri'],
                        created_at=row['created_at']
                    ),
                    disk_size=row['disk_size']
                )
                for row in rows
            ]
