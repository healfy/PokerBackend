from typing import Optional, List
from pydantic import BaseModel, EmailStr

from .consts import TablePositions, SeatStatus


class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class SeatSchema(BaseModel):
    id: int
    status: SeatStatus
    position: TablePositions
    table_id: int
    user: Optional[User]

    class Config:
        orm_mode = True


class TableSchema(BaseModel):
    name: str
    seats: List[SeatSchema]
    user_here: bool = False
    available: bool = True

    class Config:
        orm_mode = True
