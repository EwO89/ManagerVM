from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


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


class CreateUser(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
