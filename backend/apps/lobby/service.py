from sqlalchemy import select
from sqlalchemy.orm import joinedload

from backend.apps.game.models import GameHistory

from backend.apps.lobby.models import Seats, Tables
from backend.apps.lobby.consts import SeatStatus, SeatNumber
from backend.apps.lobby.errors import LobbyError
from backend.core.service import AbstractService
from backend.core.database.repository import PostgresRepository


class LobbyService(AbstractService):

    def __init__(self, repository: PostgresRepository):
        self.repository = repository

    async def reserve_seat(self, table_id: int, user_id: int) -> int:
        async with self.repository.atomic():
            seat = await self.repository.get_first(
                Seats,
                custom_filter=[
                    Seats.table_id == table_id, Seats.status == SeatStatus.FREE
                ]
            )
            if not seat:
                raise LobbyError("No available seat")
            if seat.user_id == user_id:
                raise LobbyError("You are already in this table")
            return await self.repository.update(
                Seats,
                custom_filter=[Seats.id == seat.id],
                values={'user_id': user_id, 'status': SeatStatus.RESERVED}
            )

    async def create_table(self, name: str) -> int:
        async with self.repository.atomic():
            table = await self.repository.save(Tables, {'name': name})
            await self.repository.bulk_insert(
                Seats, [{'table_id': table.id, 'number': seat_number} for seat_number in SeatNumber]
            )
            await self.repository.save(GameHistory, {'table_id': table.id})
            return table.id

    async def get_table(self, pk: int) -> Tables:
        smt = select(Tables).where(Tables.id == pk).options(joinedload(Tables.seats).subqueryload(Seats.user))
        result = await self.repository.session.scalars(smt)
        return result.first()

    async def get_tables(self):
        result = await self.repository.find_with_join(Tables, Tables.seats)
        data = []
        for table in result.fetchall():
            data.append({
                'seats': len(table.seats),
                "available": len([s for s in table.seats if s.status == SeatStatus.FREE]) > 0,
                "id": table.id,
                'name': table.name
            })
        return data
