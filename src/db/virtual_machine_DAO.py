import sqlite3
from typing import List, Optional
from datetime import datetime
from src.schemas import VirtualMachine, VirtualMachineCreate, VMDisk, VMDiskCreate


class VirtualMachineDAO:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS virtual_machine (
                    vm_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ram INTEGER NOT NULL,
                    cpu INTEGER NOT NULL,
                    description TEXT,
                    uri TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS vm_disk (
                    disk_id INTEGER PRIMARY KEY,
                    vm_id INTEGER NOT NULL,
                    disk_size INTEGER NOT NULL,
                    FOREIGN KEY (vm_id) REFERENCES virtual_machine(vm_id)
                );
            """)

    def create_vm(self, vm: VirtualMachineCreate) -> int:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO virtual_machine (name, ram, cpu, description, uri, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (vm.name, vm.ram, vm.cpu, vm.description, vm.uri, datetime.utcnow()))
            vm_id = cursor.lastrowid
            for disk in vm.hard_disks:
                cursor.execute("""
                    INSERT INTO vm_disk (vm_id, disk_size)
                    VALUES (?, ?)
                """, (vm_id, disk.disk_size))
            return vm_id

    def get_vm(self, vm_id: int) -> Optional[VirtualMachine]:
        vm_row = self.conn.execute("""
            SELECT * FROM virtual_machine WHERE vm_id = ?
        """, (vm_id,)).fetchone()

        if vm_row is None:
            return None

        disks = self.conn.execute("""
            SELECT * FROM vm_disk WHERE vm_id = ?
        """, (vm_id,)).fetchall()

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

    def update_vm(self, vm_id: int, vm: VirtualMachineCreate):
        with self.conn:
            self.conn.execute("""
                UPDATE virtual_machine SET name = ?, ram = ?, cpu = ?, description = ?, uri = ?
                WHERE vm_id = ?
            """, (vm.name, vm.ram, vm.cpu, vm.description, vm.uri, vm_id))

            self.conn.execute("""
                DELETE FROM vm_disk WHERE vm_id = ?
            """, (vm_id,))
            for disk in vm.hard_disks:
                self.conn.execute("""
                    INSERT INTO vm_disk (vm_id, disk_size)
                    VALUES (?, ?)
                """, (vm_id, disk.disk_size))

    def delete_vm(self, vm_id: int):
        with self.conn:
            self.conn.execute("""
                DELETE FROM virtual_machine WHERE vm_id = ?
            """, (vm_id,))
            self.conn.execute("""
                DELETE FROM vm_disk WHERE vm_id = ?
            """, (vm_id,))

    def list_vms(self) -> List[VirtualMachine]:
        vm_rows = self.conn.execute("""
            SELECT * FROM virtual_machine
        """).fetchall()

        vms = []
        for vm_row in vm_rows:
            disks = self.conn.execute("""
                SELECT * FROM vm_disk WHERE vm_id = ?
            """, (vm_row['vm_id'],)).fetchall()

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
