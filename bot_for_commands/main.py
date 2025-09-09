import asyncio
import logging
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from bot_for_commands.config_reader import config
from bot_for_commands.database.common import create_tables
from bot_for_commands.database.crud import chat
from bot_for_commands.cache import Cache
from bot_for_commands.menu import set_commands
from bot_for_commands.handlers import main_handlers, answers, change_rights, data
from bot_for_commands.handlers.trigger import (
    create as trigger_create,
    remove as trigger_remove,
    show as trigger_show,
)
from bot_for_commands.handlers.action import (
    create as action_create,
    remove as action_remove,
    show as action_show,
)
from bot_for_commands.handlers.welcome import (
    create as welcome_create,
    remove as welcome_remove,
    show as welcome_show,
)
from bot_for_commands.middlewares import ChatNotInDBMiddleware


async def main(bot: Bot, db_engine: AsyncEngine, cache: Cache):
    db_session = AsyncSession(db_engine, expire_on_commit=False)

    dispatcher = Dispatcher(
        db_session=db_session,
        cache=cache,
    )
    dispatcher.update.outer_middleware(
        ChatNotInDBMiddleware()
    )
    dispatcher.include_routers(
        main_handlers.router,
        trigger_create.router, trigger_remove.router, trigger_show.router,
        action_create.router, action_remove.router, action_show.router,
        welcome_create.router, welcome_remove.router, welcome_show.router,
        change_rights.router,
        data.router,
        answers.router,
    )

    await create_tables(db_engine)
    cache.reload(await chat.get_all(db_session))

    await set_commands(bot)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=config.log_level)

    asyncio.run(main(
        bot = Bot(token=config.bot_token.get_secret_value()),
        db_engine=create_async_engine(config.db_address.get_secret_value()),
        cache=Cache(),
    ))

