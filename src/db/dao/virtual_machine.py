import asyncpg
from typing import List, Optional
from src.schemas import VirtualMachine, VirtualMachineCreate, VMDisk


class VirtualMachineDAO:
    def __init__(self, pool):
        self.pool = pool

    async def create_vm(self, vm: VirtualMachineCreate) -> int:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                vm_id = await conn.fetchval("""
                    INSERT INTO virtual_machine (name, ram, cpu, description, uri, created_at)
                    VALUES ($1, $2, $3, $4, $5, NOW()) RETURNING vm_id
                """, vm.name, vm.ram, vm.cpu, vm.description, vm.uri)

                for disk in vm.hard_disks:
                    await conn.execute("""
                        INSERT INTO vm_disk (vm_id, disk_size)
                        VALUES ($1, $2)
                    """, vm_id, disk.disk_size)

                return vm_id

    async def get_vm(self, vm_id: int) -> Optional[VirtualMachine]:
        async with self.pool.acquire() as conn:
            vm_row = await conn.fetchrow("""
                SELECT * FROM virtual_machine WHERE vm_id = $1
            """, vm_id)

            if vm_row is None:
                return None

            disks = await conn.fetch("""
                SELECT * FROM vm_disk WHERE vm_id = $1
            """, vm_id)

            hard_disks = [VMDisk(**dict(disk)) for disk in disks]

            return VirtualMachine(
                vm_id=vm_row['vm_id'],
                name=vm_row['name'],
                ram=vm_row['ram'],
                cpu=vm_row['cpu'],
                description=vm_row['description'],
                uri=vm_row['uri'],
                created_at=vm_row['created_at'],
                hard_disks=hard_disks
            )

    async def update_vm(self, vm_id: int, vm: VirtualMachineCreate):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    UPDATE virtual_machine SET name = $1, ram = $2, cpu = $3, description = $4, uri = $5
                    WHERE vm_id = $6
                """, vm.name, vm.ram, vm.cpu, vm.description, vm.uri, vm_id)

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
            await conn.execute("""
                DELETE FROM virtual_machine WHERE vm_id = $1
            """, vm_id)

    async def list_vms(self) -> List[VirtualMachine]:
        async with self.pool.acquire() as conn:
            vm_rows = await conn.fetch("""
                SELECT * FROM virtual_machine
            """)

            vms = []
            for vm_row in vm_rows:
                disks = await conn.fetch("""
                    SELECT * FROM vm_disk WHERE vm_id = $1
                """, vm_row['vm_id'])

                hard_disks = [VMDisk(**dict(disk)) for disk in disks]

                vms.append(VirtualMachine(
                    vm_id=vm_row['vm_id'],
                    name=vm_row['name'],
                    ram=vm_row['ram'],
                    cpu=vm_row['cpu'],
                    description=vm_row['description'],
                    uri=vm_row['uri'],
                    created_at=vm_row['created_at'],
                    hard_disks=hard_disks
                ))

            return vms
