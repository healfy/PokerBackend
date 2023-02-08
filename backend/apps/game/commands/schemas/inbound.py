from pydantic import BaseModel
from starlette.websockets import WebSocket

from backend.apps.game.commands.consts import BaseCommand, CommandTypes


class InboundPayLoadData(BaseModel):

    class Config:
        use_enum_values = True


class InboundPayLoad(BaseModel):
    command: BaseCommand
    data: InboundPayLoadData

    class Config:
        use_enum_values = True


class InboundGameMessage(BaseModel):
    command_type: CommandTypes
    payload: InboundPayLoad

    class Config:
        use_enum_values = True

    @classmethod
    async def parse_socket(cls, websocket: WebSocket):
        data = await websocket.receive_json()
        return cls(**data)
