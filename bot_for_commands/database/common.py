from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy import delete

from bot_for_commands.database.models import Base, Chat, Trigger, Action
from bot_for_commands.database.connect import with_session


async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@with_session
async def clear_tables(session: AsyncSession):
    await session.execute(delete(Chat))
    await session.execute(delete(Trigger))
    await session.execute(delete(Action))
    await session.commit()

