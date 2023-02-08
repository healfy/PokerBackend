from sqlalchemy import (
    BigInteger,
    String,
    Column,
    DateTime,
    ForeignKey,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship

from backend.core.database.base import SQLBaseModel
from .consts import SeatStatus, TablePositions, TableLimit, SeatNumber
from datetime import datetime


class Tables(SQLBaseModel):
    __tablename__ = "tables"

    name = Column(String, index=True, nullable=False)
    create_time = Column(DateTime, default=datetime.now, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    limit = Column(Enum(TableLimit), default=TableLimit.MICRO_1, nullable=False)
    seats = relationship('Seats', backref="table", cascade="all, delete", order_by="Seats.number")
    game_history = relationship('GameHistory', backref="table", cascade="all, delete")


class Seats(SQLBaseModel):
    __tablename__ = "seats"

    status = Column(Enum(SeatStatus), default=SeatStatus.FREE, nullable=False)
    position = Column(Enum(TablePositions), default=TablePositions.UNKNOWN, nullable=False)
    number = Column(Enum(SeatNumber), nullable=False)
    table_id = Column(BigInteger, ForeignKey("tables.id", ondelete='CASCADE'))
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="seat", cascade="all, delete")
