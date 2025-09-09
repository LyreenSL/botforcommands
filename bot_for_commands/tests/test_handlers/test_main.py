from aiogram.filters import Command

from bot_for_commands.handlers.main_handlers import cmd_help, cmd_cancel
from bot_for_commands.handlers.trigger.create import create_trigger
from bot_for_commands.states import TriggerCreateState
from bot_for_commands.tests.test_handlers.common import make_bot


async def test_help():
    bot = await make_bot(cmd_help, Command(commands=['help', 'start']))
    with open('helper.txt', 'r') as f:
        assert await bot.get_answer(text='/help') == f.read()


async def test_cancel():
    bot1 = await make_bot(create_trigger, Command(commands=['trigger_add']))
    await bot1.get_answer(text='/trigger_add')
    assert await bot1.get_context().get_state() == TriggerCreateState.set_word

    bot2 = await make_bot(cmd_cancel, Command(commands=['cancel']), state_from_bot=bot1)
    assert await bot2.get_answer(text='/cancel') == 'Отменено'

    bot3 = await make_bot(cmd_cancel, Command(commands=['cancel']))
    assert await bot3.get_answer(text='/cancel') == 'Нечего отменять'

