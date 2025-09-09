import json
from io import BytesIO
from aiogram import F
from aiogram.filters import Command
from aiogram_tests.types.dataset import MESSAGE, CHAT, MESSAGE_WITH_DOCUMENT, DOCUMENT

from bot_for_commands.handlers.data import data_get, data_set, set_json
from bot_for_commands.states import SetDataState
from bot_for_commands.database.crud import chat, trigger, action
from bot_for_commands.tests.test_handlers.common import make_bot
from bot_for_commands.tests.inputs import chat_create_input, trigger_create_input, action_create_input


def make_download_method(expected_file_id, data):
    async def download(document) -> BytesIO:
        if document.file_id == expected_file_id:
            return BytesIO(data)
    return download


async def fill_data(session, cache):
    cache.write_chat(
        await chat.create(session, **chat_create_input)
    )
    cache.write_trigger(
        await trigger.create(session, **trigger_create_input)
    )
    cache.write_action(
        await action.create(session, **action_create_input)
    )


async def test_data_get(test_session, test_cache):
    await fill_data(test_session, test_cache)

    bot = await make_bot(data_get, Command(commands=['data_get']), cache=test_cache)
    document = (
        await bot.query(
            MESSAGE.as_object(
                text='/data_get',
                chat=CHAT.as_object(id=chat_create_input['id'])
            )
        )
    ).send_document.fetchone().document
    assert json.loads(document.data) == test_cache.read_chat(chat_create_input['id'])

    return document


async def test_data_set(test_session, test_cache):
    document = await test_data_get(test_session, test_cache)

    bot1 = await make_bot(data_set, Command(commands=['data_set']))
    assert await bot1.get_answer(text='/data_set') == 'Отправьте json-файл'
    assert await bot1.get_context().get_state() == SetDataState.set_json

    bot2 = await make_bot(
        set_json, F.document, state_from_bot=bot1,
        db_session=test_session, cache=test_cache,
    )
    bot2._handler.bot.download = make_download_method(DOCUMENT['file_id'], document.data)
    assert (
        await bot2.query(message=MESSAGE_WITH_DOCUMENT.as_object())
    ).send_message.fetchone().text == 'Принято'

    chat1_data = test_cache.read_chat(chat_create_input['id'])
    chat2_data = test_cache.read_chat(CHAT['id'])
    del chat1_data['triggers'][trigger_create_input['word']]['id']
    del chat1_data['actions'][action_create_input['command']]['id']
    del chat2_data['triggers'][trigger_create_input['word']]['id']
    del chat2_data['actions'][action_create_input['command']]['id']
    assert chat1_data == chat2_data

    return bot2


async def test_data_set_duplicate(test_session, test_cache):
    bot2 = await test_data_set(test_session, test_cache)

    assert (
        await bot2.query(message=MESSAGE_WITH_DOCUMENT.as_object())
    ).send_message.fetchone().text == 'Принято'

