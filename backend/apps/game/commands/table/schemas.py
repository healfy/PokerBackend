from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from backend.apps.game.commands.schemas.inbound import InboundPayLoadData
from backend.apps.game.commands.schemas.outboud import OutboundPayLoadData
from backend.apps.lobby.consts import SeatStatus, TablePositions


class InboundInfoData(InboundPayLoadData):
    table_id: int


class Wallet(BaseModel):
    amount: Decimal
    currency: str

    class Config:
        orm_mode = True
        json_encoders = {Decimal: str}


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    wallet: Wallet

    class Config:
        orm_mode = True


class Seat(BaseModel):
    id: int
    status: SeatStatus
    position: TablePositions
    user: Optional[UserProfile]

    class Config:
        orm_mode = True
        use_enum_values = True


class Table(BaseModel):
    id: int
    name: str
    seats: List[Seat]

    class Config:
        orm_mode = True


class OutboundInfoData(OutboundPayLoadData):
    table: Table
