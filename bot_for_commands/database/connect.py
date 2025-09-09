from sqlalchemy.ext.asyncio import AsyncSession


def with_session(func):
    async def wrapper(session: AsyncSession, *args, **kwargs):
        async with session:
            try:
                return await func(session=session, *args, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper

