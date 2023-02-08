from backend.apps.game.commands.base import MessageHandler
from backend.apps.game.commands.schemas.inbound import InboundGameMessage


class GameMessageHandler(MessageHandler):

    async def handle(self, message: InboundGameMessage):
        print(2222)
