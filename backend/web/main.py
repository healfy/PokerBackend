import logging.config
from asyncio import create_task
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.apps.game.task import StateManagerTask
from backend.core.database.repository import PostgresRepository
from backend.web.handlers import auth, users, table
from backend.settings import app_settings
from backend.web.websockets.game_room import ws_router

app = FastAPI()

app.include_router(auth.router, prefix="/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/v1", tags=["Users"])
app.include_router(table.router, prefix="/v1", tags=["Tables"])
app.include_router(ws_router, prefix="/ws", tags=["Test"])

# setup loggers
logging.config.fileConfig('/Users/konstantin.zavadskiy/PycharmProjects/poker_room/backend/settings/logging.cfg', disable_existing_loggers=False)


origins = ['http://localhost:3000', 'localhost:8001']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

async_engine = create_async_engine(
    app_settings.POSTGRES.dsn,
    pool_pre_ping=True,
    echo_pool=True,
)


@app.on_event("startup")
async def startup():
    app.state.settings = app_settings
    app.state.engine = async_engine
    # create_task(start_task())


@app.on_event("shutdown")
async def shutdown():
    await app.state.engine.dispose()


async def start_task():
    session_local = scoped_session(sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession))
    manager = StateManagerTask(PostgresRepository(session_local()))
    await manager.run()


def custom_openapi():
    openapi_schema = get_openapi(
        title="Api Gateway Service",
        description="Service provides access to internal services",
        version="0.0.1",
        routes=app.routes,
    )
    return openapi_schema


app.openapi_schema = custom_openapi()
