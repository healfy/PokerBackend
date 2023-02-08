from abc import ABC, abstractmethod

from backend.apps.game.commands.schemas.inbound import InboundGameMessage
from backend.apps.game.commands.schemas.outboud import OutboundGameMessage


class MessageHandler(ABC):

    @abstractmethod
    async def handle(self, message: InboundGameMessage) -> OutboundGameMessage:
        pass

