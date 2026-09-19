from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bootstrap.config.settings import get_settings


def create_engine() -> AsyncEngine:
    return create_async_engine(get_settings().database_url, echo=False)


engine = create_engine()
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def close_engine() -> None:
    await engine.dispose()
