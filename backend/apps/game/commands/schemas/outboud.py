from typing import Optional, Union
from pydantic import BaseModel

from backend.apps.game.commands.consts import CommandTypes, TableCommand, GameCommand


class OutboundPayLoadData(BaseModel):

    class Config:
        use_enum_values = True


class OutboundPayLoad(BaseModel):
    command: Union[TableCommand, GameCommand]
    data: OutboundPayLoadData

    class Config:
        use_enum_values = True


class OutboundGameMessage(BaseModel):
    command_type: CommandTypes
    payload: Optional[OutboundPayLoad] = None

    class Config:
        use_enum_values = True
