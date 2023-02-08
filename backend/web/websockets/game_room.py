import asyncio
from typing import Dict
from fastapi import WebSocket, Depends, APIRouter
from websockets.exceptions import ConnectionClosed

from backend.apps.game.commands.base import MessageHandler
from backend.apps.game.commands.consts import CommandTypes
from backend.apps.game.commands.schemas.inbound import InboundGameMessage
from backend.apps.game.commands.schemas.outboud import OutboundGameMessage
from backend.apps.user.models import User

from backend.apps.lobby.service import LobbyService
from backend.web.websockets.deps import check_access_ws, get_user_ws, get_lobby_service_ws, get_message_handlers

ws_router = APIRouter()


@ws_router.websocket("/tables")
async def get_tables(websocket: WebSocket = Depends(check_access_ws), service: LobbyService = Depends(get_lobby_service_ws)):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(await service.get_tables())
            await asyncio.sleep(2)
    except ConnectionClosed:
        print("disconnected")


@ws_router.websocket("/tables/{table_id}")
async def handle_table(
        table_id: int,
        websocket: WebSocket = Depends(check_access_ws),
        user: User = Depends(get_user_ws),
        handlers: Dict[CommandTypes, MessageHandler] = Depends(get_message_handlers)
):
    """
    1. check auth
    2. check table and table state
    3. check if command can be used
    4. save command to game history
    5. try to change table state

    """
    await websocket.accept()
    try:
        while True:
            message = await InboundGameMessage.parse_socket(websocket)
            handler = handlers[message.command_type]
            result: OutboundGameMessage = await handler.handle(message)
            await websocket.send_json(result)
    except ConnectionClosed:
        print("disconnected")
    finally:
        await websocket.close()
