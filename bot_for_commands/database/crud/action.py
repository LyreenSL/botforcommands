from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from bot_for_commands.database.crud import base
from bot_for_commands.database.models import Action
from bot_for_commands.database.exceptions import ChatDontExistError, ActionDontExistError, ActionDuplicateError


async def create(
    session: AsyncSession,
    is_interaction: bool,
    command: str,
    text: str,
    chat_id: int,
) -> Action:
    try:
        return await base.create(
            model=Action, session=session, is_interaction=is_interaction,
            command=command, text=text, chat_id=chat_id,
        )
    except IntegrityError as e:
        if "foreign key constraint fails" in str(e) and "FOREIGN KEY (`chat_id`)" in str(e):
            raise ChatDontExistError()
        elif "Duplicate entry" in str(e):
            raise ActionDuplicateError()
        else:
            raise e


async def get(
    session: AsyncSession,
    id: int,
) -> Action:
    return await base.get(model=Action, session=session, id=id)


async def update(
    session: AsyncSession,
    id: int,
    is_interaction: bool | None = None,
    command: str | None = None,
    text: str | None = None,
) -> Action:
    try:
        return await base.update(
            model=Action, session=session, id=id, is_interaction=is_interaction, command=command, text=text
        )
    except AttributeError:
        raise ActionDontExistError()


async def delete(
    session: AsyncSession,
    id: int,
) -> None:
    try:
        return await base.delete(model=Action, session=session, id=id)
    except UnmappedInstanceError:
        raise ActionDontExistError()

