from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from bot_for_commands.database.crud import base
from bot_for_commands.database.models import Chat, Trigger, Action
from bot_for_commands.database.exceptions import ChatDuplicateError, ChatDontExistError
from bot_for_commands.database.connect import with_session


async def create(
    session: AsyncSession,
    id: int,
    members_rights: bool = True,
    welcome_message: str | None = None,
    triggers: list[Trigger] = [],
    actions: list[Action] = [],
) -> Chat:
    try:
        return await base.create(
            model=Chat, session=session, id=id, members_rights=members_rights,
            welcome_message=welcome_message, triggers=triggers, actions=actions
        )
    except IntegrityError as e:
        if "Duplicate entry" in str(e):
            raise ChatDuplicateError()
        else:
            raise e


async def get(
    session: AsyncSession,
    id: int,
) -> Chat:
    return await base.get(model=Chat, session=session, id=id)


async def get_all(
    session: AsyncSession,
) -> list[Chat]:
    return await base.get_all(model=Chat, session=session)


async def update(
    session: AsyncSession,
    id: int,
    members_rights: bool | None = None,
    welcome_message: str | None = None,
    # triggers: list[Trigger] | None = None,
    # actions: list[Action] | None = None,
) -> Chat:
    try:
        return await base.update(
            model=Chat, session=session, id=id, members_rights=members_rights,
            welcome_message=welcome_message,
            # triggers=triggers, actions=actions
        )
    except AttributeError:
        raise ChatDontExistError()


async def delete(
    session: AsyncSession,
    id: int,
) -> None:
    try:
        return await base.delete(model=Chat, session=session, id=id)
    except UnmappedInstanceError:
        raise ChatDontExistError()


async def replace(
    session: AsyncSession,
    id: int,
    members_rights: bool,
    triggers: list[Trigger],
    actions: list[Action],
    welcome_message: str | None = None,
) -> Chat:
    try:
        await delete(session=session, id=id)
        return await create(
            session=session, id=id, members_rights=members_rights,
            welcome_message=welcome_message, triggers=triggers, actions=actions
        )

    except UnmappedInstanceError:
        raise ChatDontExistError()

