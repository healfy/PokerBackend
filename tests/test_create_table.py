import json

import pytest

from backend import Tables
from backend.apps.game.commands.consts import TableCommand, CommandTypes
from backend.apps.game.commands.schemas.outboud import OutboundGameMessage, OutboundPayLoad
from backend.apps.game.commands.table.schemas import OutboundInfoData, Table
from backend.apps.game.state import StartGameState
from backend.apps.lobby.service import LobbyService
from backend.apps.user.schema import UserCreateSchema, UserSchema
from backend.apps.user.service import UserService
from backend.core.database.repository import PostgresRepository


@pytest.mark.asyncio
async def test_create_table(db_session):
    service = LobbyService(PostgresRepository(db_session))
    pk = await service.create_table("Werded")
    assert pk is not None
    user_service = UserService(PostgresRepository(db_session))
    user1: UserSchema = await user_service.register(
        UserCreateSchema(
            email='werded@tut.by',
            password='Healfy1992@',
            confirm_password='Healfy1992@',
        )
    )
    user2: UserSchema = await user_service.register(
        UserCreateSchema(
            email='werded1@tut.by',
            password='Healfy1992@',
            confirm_password='Healfy1992@',
        )
    )
    user3: UserSchema = await user_service.register(
        UserCreateSchema(
            email='werde123123d1@tut.by',
            password='Healfy1992@',
            confirm_password='Healfy1992@',
        )
    )
    user4: UserSchema = await user_service.register(
        UserCreateSchema(
            email='werdwde123123d1@tut.by',
            password='Healfy1992@',
            confirm_password='Healfy1992@',
        )
    )
    await service.reserve_seat(pk, user1.id)
    await service.reserve_seat(pk, user2.id)
    await service.reserve_seat(pk, user3.id)
    await service.reserve_seat(pk, user4.id)
    state = StartGameState(PostgresRepository(db_session), pk)
    await state.make_transition()
    table: Tables = await state.repository.get_table(pk)
    print(table)
    message = OutboundGameMessage(
            command_type=CommandTypes.TABLE,
            payload=OutboundPayLoad(command=TableCommand.INFO, data=OutboundInfoData(table=Table.from_orm(table)))
        )
    print(message)

