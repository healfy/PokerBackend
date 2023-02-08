from decimal import Decimal

from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DECIMAL, BigInteger, ForeignKey, Enum
from backend.core.database.base import SQLBaseModel
from .consts import Currency


class User(SQLBaseModel):

    __tablename__ = "users"

    email = Column(String(length=100), unique=True, nullable=False)
    password = Column(String(length=100), nullable=False)
    seat = relationship("Seats", back_populates="user", uselist=False, cascade="all, delete")
    wallet = relationship('Wallet', back_populates="user", uselist=False, cascade="all, delete")


class Wallet(SQLBaseModel):

    __tablename__ = "wallets"

    amount = Column(DECIMAL(15, 2), default=Decimal("0"), nullable=False)
    currency = Column(Enum(Currency), default=Currency.USD, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="wallet", cascade="all, delete")
