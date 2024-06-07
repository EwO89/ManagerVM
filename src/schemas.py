from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# Схемы для виртуальных машин

class VirtualMachineCreate(BaseModel):
    name: str
    ram: int
    cpu: int
    description: Optional[str] = None


class VirtualMachine(BaseModel):
    vm_id: int
    name: str
    ram: int
    cpu: int
    description: Optional[str] = None
    created_at: datetime




class VMDiskCreate(BaseModel):
    vm_id: int
    disk_size: int


class VMDisk(BaseModel):
    disk_id: int
    vm_id: int
    disk_size: int




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
