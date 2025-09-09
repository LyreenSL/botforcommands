from aiogram import Dispatcher
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from bot_for_commands.middlewares import ChatNotInDBMiddleware


class MyMockedBot(MockedBot):
    def get_context(self):
        return self._handler.dp.fsm.get_context(
            self._handler.bot,
            12345678,
            12345678,
        )

    async def get_answer(self, **kwargs):
        return (
            await self.query(message=MESSAGE.as_object(**kwargs))
        ).send_message.fetchone().text


async def make_bot(handler_function, *args, state_from_bot=None, db_session=None, cache=None, **kwargs):
    return MyMockedBot(
        MessageHandler(
            handler_function,
            *args, **kwargs,
            state = await state_from_bot.get_context().get_state() if state_from_bot else None,
            state_data = await state_from_bot.get_context().get_data() if state_from_bot else {},
            dp = Dispatcher(db_session=db_session, cache=cache),
            dp_middlewares=[ChatNotInDBMiddleware()]
        )
    )

