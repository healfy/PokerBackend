from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
)
from datetime import datetime
from backend.core.database.base import SQLBaseModel
from .consts import GameState


class GameHistory(SQLBaseModel):
    __tablename__ = "game_histories"

    create_time = Column(DateTime, default=datetime.now, index=True, nullable=False)
    table_id = Column(BigInteger, ForeignKey("tables.id"))
    data = Column(JSON, nullable=True)
    state = Column(Enum(GameState), default=GameState.INITIAL, nullable=False, index=True)
