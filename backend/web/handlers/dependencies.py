import jwt
from fastapi import Depends, Request, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import State

from backend.apps.lobby.service import LobbyService
from backend.core.database.repository import PostgresRepository
from backend.apps.auth import AuthService
from backend.apps.user.service import UserService
from backend.settings import AppSettings


def get_state(request: Request) -> State:
    return request.app.state


def get_settings(state: State = Depends(get_state)) -> AppSettings:
    return state.settings


def get_engine(state: State = Depends(get_state)) -> AsyncSession:
    return state.engine


async def get_session(engine: AsyncEngine = Depends(get_engine)) -> AsyncSession:
    session_local = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with session_local() as session:
        yield session


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(PostgresRepository(session))


def get_auth_service(settings: AppSettings = Depends(get_settings)) -> AuthService:
    return AuthService(settings.AUTH)


def get_lobby_service(session: AsyncSession = Depends(get_session)) -> LobbyService:
    return LobbyService(PostgresRepository(session))


def check_access(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=403, detail="Access Denied")
    try:
        user_id: str = auth_service.decode_access_token(token)
        if not user_id:
            raise HTTPException(status_code=403, detail="Access Denied")
    except jwt.ExpiredSignatureError:
        token = request.cookies.get('refresh_token')
        token = auth_service.refresh_token(token)
    request.state.token = token


def set_cookie(request: Request, response: Response):
    response.set_cookie(key="access_token", value=request.state.token, httponly=True)


def get_user_id(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.decode_access_token(request.cookies.get('access_token'))
