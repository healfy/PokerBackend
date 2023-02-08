import jwt
from typing import Dict
from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket

from backend.apps.auth import AuthService
from backend.apps.game.commands.base import MessageHandler
from backend.apps.game.commands.consts import CommandTypes
from backend.apps.game.commands.game.handlers import GameMessageHandler
from backend.apps.game.commands.table.handlers import TableMessageHandler
from backend.apps.lobby.service import LobbyService
from backend.apps.user.service import UserService
from backend.core.database.repository import PostgresRepository


def get_engine(websocket: WebSocket) -> AsyncSession:
    return websocket.app.state.engine


async def get_session(engine: AsyncEngine = Depends(get_engine)) -> AsyncSession:
    session_local = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with session_local() as session:
        yield session


def get_auth_service(websocket: WebSocket) -> AuthService:
    return AuthService(websocket.app.state.settings.AUTH)


def get_table_message_handler(session: AsyncSession = Depends(get_session)) -> TableMessageHandler:
    return TableMessageHandler(PostgresRepository(session))


def get_game_message_handler() -> GameMessageHandler:
    return GameMessageHandler()


def get_message_handlers(
        game: GameMessageHandler = Depends(get_game_message_handler),
        table: TableMessageHandler = Depends(get_table_message_handler)
) -> Dict[CommandTypes, MessageHandler]:
    return {
        CommandTypes.GAME: game,
        CommandTypes.TABLE: table,
    }


async def check_access_ws(websocket: WebSocket, auth_service: AuthService = Depends(get_auth_service)) -> WebSocket:
    token = websocket.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        user_id: str = auth_service.decode_access_token(token)
        if not user_id:
            raise HTTPException(status_code=403, detail="Access Denied")
    except jwt.ExpiredSignatureError:
        token = websocket.cookies.get('refresh_token')
        new_token = auth_service.refresh_token(token)
        websocket.cookies.update(key='access_token', value=new_token)
        websocket.cookies.update(key='refresh_token', value=token)
    return websocket


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(PostgresRepository(session))


def get_lobby_service_ws(session: AsyncSession = Depends(get_session)) -> LobbyService:
    return LobbyService(PostgresRepository(session))


async def get_user_ws(
        websocket: WebSocket,
        auth_service: AuthService = Depends(get_auth_service),
        user_service: UserService = Depends(get_user_service),
):
    token = websocket.cookies.get('access_token')
    user_id: str = auth_service.decode_access_token(token)
    return await user_service.get_user(int(user_id))
