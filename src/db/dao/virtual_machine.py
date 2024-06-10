import asyncpg
from typing import List, Optional
from src.schemas import VirtualMachineModel, VirtualMachineCreate, VMDiskModel
from src.db.dao.base import BaseDAO

class VirtualMachineDAO(BaseDAO):
    def __init__(self, pool):
        self.table_name = "virtual_machine"
        super().__init__(pool)

    async def create_vm(self, vm: VirtualMachineCreate) -> int:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                vm_id = await conn.fetchval(f"""
                    INSERT INTO {self.table_name} (name, ram, cpu, description, created_at)
                    VALUES ($1, $2, $3, $4, NOW()) RETURNING vm_id
                """, vm.name, vm.ram, vm.cpu, vm.description)

                for disk in vm.hard_disks:
                    await conn.execute("""
                        INSERT INTO vm_disk (vm_id, disk_size)
                        VALUES ($1, $2)
                    """, vm_id, disk.disk_size)

                return vm_id

    async def get_vm(self, vm_id: int) -> Optional[VirtualMachineModel]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT 
                    vm.*, 
                    disk.disk_id, 
                    disk.disk_size
                FROM 
                    {self.table_name} AS vm
                LEFT JOIN 
                    vm_disk AS disk ON vm.vm_id = disk.vm_id
                WHERE 
                    vm.vm_id = $1
            """, vm_id)

            if not rows:
                return None

            disks = [VMDiskModel(disk_id=row['disk_id'], vm_id=row['vm_id'], disk_size=row['disk_size']) for row in rows
                     if row['disk_id'] is not None]

            vm_row = rows[0]
            return VirtualMachineModel(
                vm_id=vm_row['vm_id'],
                name=vm_row['name'],
                ram=vm_row['ram'],
                cpu=vm_row['cpu'],
                description=vm_row['description'],
                created_at=vm_row['created_at'],
                hard_disks=disks
            )

    async def update_vm(self, vm_id: int, vm: VirtualMachineCreate):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(f"""
                    UPDATE {self.table_name} SET name = $1, ram = $2, cpu = $3, description = $4
                    WHERE vm_id = $5
                """, vm.name, vm.ram, vm.cpu, vm.description, vm_id)

                await conn.execute("""
                    DELETE FROM vm_disk WHERE vm_id = $1
                """, vm_id)
                for disk in vm.hard_disks:
                    await conn.execute("""
                        INSERT INTO vm_disk (vm_id, disk_size)
                        VALUES ($1, $2)
                    """, vm_id, disk.disk_size)

    async def delete_vm(self, vm_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                DELETE FROM {self.table_name} WHERE vm_id = $1
            """, vm_id)

    async def list_vms(self) -> List[VirtualMachineModel]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT 
                    vm.*, 
                    disk.disk_id, 
                    disk.disk_size
                FROM 
                    {self.table_name} AS vm
                LEFT JOIN 
                    vm_disk AS disk ON vm.vm_id = disk.vm_id
                ORDER BY 
                    vm.vm_id
            """)

            vms = []
            current_vm = None
            for row in rows:
                if current_vm is None or current_vm.vm_id != row['vm_id']:
                    if current_vm is not None:
                        vms.append(current_vm)
                    current_vm = VirtualMachineModel(
                        vm_id=row['vm_id'],
                        name=row['name'],
                        ram=row['ram'],
                        cpu=row['cpu'],
                        description=row['description'],
                        created_at=row['created_at'],
                        hard_disks=[]
                    )
                if row['disk_id'] is not None:
                    current_vm.hard_disks.append(
                        VMDiskModel(disk_id=row['disk_id'], vm_id=row['vm_id'], disk_size=row['disk_size']))
            if current_vm is not None:
                vms.append(current_vm)

            return vms
