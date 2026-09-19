from sqlalchemy.ext.asyncio import AsyncEngine

from modules.conversation.infrastructure.persistence.models import Base


async def create_tables(engine: AsyncEngine) -> None:
    # Development bootstrap; Alembic remains the schema migration authority.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
