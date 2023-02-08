from typing import Dict, Callable

from backend.apps.game.commands.base import MessageHandler
from backend.apps.game.commands.consts import BaseCommand, TableCommand, CommandTypes
from backend.apps.game.commands.schemas.inbound import InboundGameMessage
from backend.apps.game.commands.schemas.outboud import OutboundGameMessage, OutboundPayLoad
from backend.apps.game.commands.table.schemas import InboundInfoData, OutboundInfoData, Table
from backend.core.database.repository import PostgresRepository


class TableMessageHandler(MessageHandler):

    def __init__(self, repository: PostgresRepository):
        self.repository = repository
        self._mapping: Dict[BaseCommand, Callable] = {
            TableCommand.INFO: self._handle_info
        }

    async def handle(self, message: InboundGameMessage) -> OutboundGameMessage:
        func = self._mapping[message.payload.command]
        return await func(message.payload.data)

    async def _handle_info(self, data: InboundInfoData) -> OutboundGameMessage:
        table_data = await self.repository.get_table(data.table_id)
        return OutboundGameMessage(
            command_type=CommandTypes.TABLE,
            payload=OutboundPayLoad(command=TableCommand.INFO, data=OutboundInfoData(table=Table.from_orm(table_data)))
        )
