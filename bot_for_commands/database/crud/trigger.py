from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from bot_for_commands.database.crud import base
from bot_for_commands.database.models import Trigger
from bot_for_commands.database.exceptions import ChatDontExistError, TriggerDontExistError, TriggerDuplicateError


async def create(
    session: AsyncSession,
    word: str,
    answer: str,
    chat_id: int,
) -> Trigger:
    try:
        return await base.create(model=Trigger, session=session, word=word, answer=answer, chat_id=chat_id)
    except IntegrityError as e:
        if "foreign key constraint fails" in str(e) and "FOREIGN KEY (`chat_id`)" in str(e):
            raise ChatDontExistError()
        elif "Duplicate entry" in str(e):
            raise TriggerDuplicateError()
        else:
            raise e


async def get(
    session: AsyncSession,
    id: int,
) -> Trigger:
    return await base.get(model=Trigger, session=session, id=id)


async def update(
    session: AsyncSession,
    id: int,
    word: str | None = None,
    answer: str | None = None,
) -> Trigger:
    try:
        return await base.update(model=Trigger, session=session, id=id, word=word, answer=answer)
    except AttributeError:
        raise TriggerDontExistError()


async def delete(
    session: AsyncSession,
    id: int,
) -> None:
    try:
        return await base.delete(model=Trigger, session=session, id=id)
    except UnmappedInstanceError:
        raise TriggerDontExistError()

