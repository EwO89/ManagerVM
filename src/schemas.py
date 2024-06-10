from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VMDiskCreate(BaseModel):
    disk_id: int
    disk_size: int


class VMDisk(BaseModel):
    disk_id: int
    vm_id: int
    disk_size: int


class VirtualMachineCreate(BaseModel):
    name: str
    ram: int
    cpu: int
    description: Optional[str] = None
    hard_disks: List[VMDiskCreate] = []


class VirtualMachine(BaseModel):
    vm_id: int
    name: str
    ram: int
    cpu: int
    description: Optional[str] = None
    created_at: datetime
    hard_disks: List[VMDisk] = []


class WSConnectionHistoryCreate(BaseModel):
    vm_id: int
    connected_at: datetime


class WSConnectionHistory(BaseModel):
    id: int
    vm_id: int
    connected_at: datetime
    disconnected_at: Optional[datetime] = None


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
