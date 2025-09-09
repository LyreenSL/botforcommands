from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot_for_commands.database.models import TBase
from bot_for_commands.database.connect import with_session


@with_session
async def create(session: AsyncSession, model: TBase, **kwargs):
    inst = model(**kwargs)
    session.add(inst)
    await session.commit()
    return inst


@with_session
async def get(session: AsyncSession, model: TBase, id: int):
    return await session.get(model, id)


@with_session
async def get_all(session: AsyncSession, model: TBase):
    return (await session.scalars(
        select(model)
    )).all()


@with_session
async def update(session: AsyncSession, model: TBase, id: int, **kwargs):
    inst = await session.get(model, id)
    for key, value in kwargs.items():
        if value is not None:
            setattr(inst, key, value)
    await session.commit()
    return inst


@with_session
async def delete(model: TBase, session: AsyncSession, id: int):
    await session.delete(
        await session.get(model, id)
    )
    await session.commit()

