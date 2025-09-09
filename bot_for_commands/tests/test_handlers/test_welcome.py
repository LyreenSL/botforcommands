from aiogram import F
from aiogram.filters import Command
from aiogram_tests.types.dataset import (
    MESSAGE,
    MESSAGE_WITH_PHOTO, PHOTO, 
    MESSAGE_WITH_VIDEO, VIDEO,
    MESSAGE_WITH_STICKER, STICKER,
)

from bot_for_commands.handlers.welcome.create import welcome_add, set_welcome
from bot_for_commands.handlers.welcome.show import welcome_show
from bot_for_commands.handlers.welcome.remove import welcome_remove
from bot_for_commands.states import SetWelcomeState
from bot_for_commands.database.crud import chat
from bot_for_commands.tests.test_handlers.common import make_bot


def read_welcome(cache):
    return cache.read_chat(12345678)['welcome_message']


async def test_welcome_create(test_session, test_cache):
    bot1 = await make_bot(welcome_add, Command(commands=['welcome_add']))
    assert await bot1.get_answer(text='/welcome_add') == 'Введите приветственное сообщение'
    assert await bot1.get_context().get_state() == SetWelcomeState.set_welcome

    bot2 = await make_bot(
        set_welcome, F.photo | F.video | F.sticker  | F.animation | F.text,
        state_from_bot=bot1, db_session=test_session, cache=test_cache
    )
    assert await bot2.get_answer(text='aaaaa') == 'Добавлено'
    assert not await bot2.get_context().get_state()
    assert (
        (await chat.get(test_session, id=12345678)).welcome_message ==
        read_welcome(test_cache) ==
        'txt:aaaaa'
    )

    await bot2.query(
        message=MESSAGE_WITH_VIDEO.as_object(caption='aaabaaa')
    )
    assert read_welcome(test_cache) == f'vid:{VIDEO.as_object().file_id};aaabaaa'

    await bot2.query(
        message=MESSAGE_WITH_STICKER.as_object()
    )
    assert read_welcome(test_cache) == f'stk:{STICKER.as_object().file_id}'

    await bot2.query(
        message=MESSAGE_WITH_PHOTO.as_object(caption='aaa;aaa')
    )
    assert read_welcome(test_cache) == f'pht:{PHOTO.as_object().file_id};aaa;aaa'


async def test_welcome_show(test_session, test_cache):
    await test_welcome_create(test_session, test_cache)

    bot = await make_bot(
        welcome_show, F.new_chat_members | F.text == '/welcome_show', cache=test_cache
    )
    response = (
        await bot.query(MESSAGE.as_object(text='/welcome_show'))
    ).send_photo.fetchone()
    assert response.photo == PHOTO.as_object().file_id
    assert response.caption == 'aaa;aaa'


async def test_welcome_delete(test_session, test_cache):
    await test_welcome_create(test_session, test_cache)

    bot = await make_bot(
        welcome_remove, Command(commands=['welcome_remove']), db_session=test_session, cache=test_cache
    )
    assert await bot.get_answer(text='/welcome_remove') == 'Удалено'
    assert not read_welcome(test_cache)

