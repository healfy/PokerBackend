import pytest
import asyncio
from sqlalchemy.orm import sessionmaker
import pytest_asyncio
from backend.core.database.base import metadata

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.settings import app_settings


__all__ = [
    'engine',
    'setup_database',
    'get_session',
]


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session", autouse=True)
def engine():
    async_engine = create_async_engine(
        app_settings.POSTGRES.dsn,
        pool_pre_ping=True,
        echo_pool=True,
    )
    return async_engine


@pytest_asyncio.fixture(scope='session', name='setup_database', autouse=True)
async def setup_database(engine):
    async with engine.connect() as connection:
        async  with connection.begin():
            await connection.run_sync(metadata.drop_all)
            await connection.run_sync(metadata.create_all)


@pytest_asyncio.fixture(name="db_session")
async def get_session(engine, setup_database):
    session_local = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with session_local() as session:
        yield session
