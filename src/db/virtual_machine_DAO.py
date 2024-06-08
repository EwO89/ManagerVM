import asyncpg
from typing import List, Optional
from datetime import datetime
from src.schemas import VirtualMachine, VirtualMachineCreate, VMDisk


class VirtualMachineDAO:
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def connect(self):
        self.conn = await asyncpg.connect(self.dsn)

    async def close(self):
        await self.conn.close()

    async def create_tables(self):
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS virtual_machine (
                vm_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                ram INTEGER NOT NULL,
                cpu INTEGER NOT NULL,
                description TEXT,
                uri TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vm_disk (
                disk_id SERIAL PRIMARY KEY,
                vm_id INTEGER NOT NULL,
                disk_size INTEGER NOT NULL,
                FOREIGN KEY (vm_id) REFERENCES virtual_machine(vm_id) ON DELETE CASCADE
            );
        """)

    async def create_vm(self, vm: VirtualMachineCreate) -> int:
        async with self.conn.transaction():
            vm_id = await self.conn.fetchval("""
                INSERT INTO virtual_machine (name, ram, cpu, description, uri)
                VALUES ($1, $2, $3, $4, $5) RETURNING vm_id
            """, vm.name, vm.ram, vm.cpu, vm.description, vm.uri)

            for disk in vm.hard_disks:
                await self.conn.execute("""
                    INSERT INTO vm_disk (vm_id, disk_size)
                    VALUES ($1, $2)
                """, vm_id, disk.disk_size)

            return vm_id

    async def get_vm(self, vm_id: int) -> Optional[VirtualMachine]:
        vm_row = await self.conn.fetchrow("""
            SELECT * FROM virtual_machine WHERE vm_id = $1
        """, vm_id)

        if vm_row is None:
            return None

        disks = await self.conn.fetch("""
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
        async with self.conn.transaction():
            await self.conn.execute("""
                UPDATE virtual_machine SET name = $1, ram = $2, cpu = $3, description = $4, uri = $5
                WHERE vm_id = $6
            """, vm.name, vm.ram, vm.cpu, vm.description, vm.uri, vm_id)

            await self.conn.execute("""
                DELETE FROM vm_disk WHERE vm_id = $1
            """, vm_id)
            for disk in vm.hard_disks:
                await self.conn.execute("""
                    INSERT INTO vm_disk (vm_id, disk_size)
                    VALUES ($1, $2)
                """, vm_id, disk.disk_size)

    async def delete_vm(self, vm_id: int):
        await self.conn.execute("""
            DELETE FROM virtual_machine WHERE vm_id = $1
        """, vm_id)

    async def list_vms(self) -> List[VirtualMachine]:
        vm_rows = await self.conn.fetch("""
            SELECT * FROM virtual_machine
        """)

        vms = []
        for vm_row in vm_rows:
            disks = await self.conn.fetch("""
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
