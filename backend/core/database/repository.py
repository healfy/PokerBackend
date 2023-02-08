import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Type, Union

from sqlalchemy import insert, select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import ClauseElement

from backend.apps.lobby.models import Tables, Seats
from backend.apps.user.models import User
from backend.core.database.base import SQLBaseModel

logger = logging.getLogger()

QUERY = Optional[List[Union[ClauseElement, Any]]]


class PostgresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def atomic(self) -> AsyncSessionTransaction:
        async with self.session.begin():
            yield

    async def save(self, clazz: Type[SQLBaseModel], values: Dict) -> SQLBaseModel:
        result = await self.session.execute(insert(clazz).values(**values).returning(clazz))
        return result.scalar_one()

    async def bulk_insert(self, clazz: Type[SQLBaseModel], values: List[dict]):
        await self.session.execute(insert(clazz), values)

    async def update(self, clazz: Type[SQLBaseModel], values: Dict, custom_filter: QUERY = ()) -> SQLBaseModel:
        result = await self.session.execute(update(clazz).where(and_(True, *custom_filter)).values(**values).returning(clazz))
        return result.scalar_one_or_none()

    async def find_one(self, clazz: Type[SQLBaseModel], *, custom_filter: QUERY = ()) -> Optional[SQLBaseModel]:
        smt = await self.session.execute(select(clazz).where(and_(True, *custom_filter)))
        return smt.scalar_one_or_none()

    async def get_first(self, clazz: Type[SQLBaseModel], *, custom_filter: QUERY = ()) -> Optional[SQLBaseModel]:
        smt = await self.session.execute(select(clazz).where(and_(True, *custom_filter)).limit(1).order_by(clazz.id))
        return smt.scalar_one_or_none()

    async def find_with_join(self, clazz: Type[SQLBaseModel], column, *, custom_filter: QUERY = ()):
        return await self.session.scalars(select(clazz).where(and_(True, *custom_filter)).options(selectinload(column)))

    async def get_table(self, table_id: int) -> Tables:
        smt = select(Tables).where(Tables.id == table_id).options(
            joinedload(Tables.seats).subqueryload(Seats.user).subqueryload(User.wallet))
        result = await self.session.scalars(smt)
        return result.first()
