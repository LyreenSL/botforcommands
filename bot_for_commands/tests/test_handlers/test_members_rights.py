from aiogram import F
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.types import Chat
from aiogram_tests.types.dataset import CHAT, USER, CHAT_MEMBER, MESSAGE
from aiogram_tests.types.dataset.base import DatasetItem

from bot_for_commands.handlers.trigger.create import create_trigger
from bot_for_commands.handlers.change_rights import members_rights_off, members_rights_on, _filters
from bot_for_commands.tests.test_handlers.common import make_bot
from bot_for_commands.cache import Cache
from bot_for_commands.filters import RightsFilter
from bot_for_commands.database.crud import chat


async def test_change_rights(test_session, test_cache):
    bot1 = await make_bot(
        members_rights_off,
        _filters, Command(commands=['members_rights_off']),
        cache=test_cache, db_session=test_session,
    )
    assert await bot1.get_answer(text='/members_rights_off') == 'Пользователи лишены права редактирования'
    assert not (await chat.get(test_session, 12345678)).members_rights
    assert not test_cache.read_chat(12345678)['members_rights']

    bot2 = await make_bot(
        members_rights_on,
        _filters, Command(commands=['members_rights_on']),
        cache=test_cache, db_session=test_session,
    )
    assert await bot2.get_answer(text='/members_rights_on') == 'Пользователям даны права редактирования'
    assert (await chat.get(test_session, 12345678)).members_rights
    assert test_cache.read_chat(12345678)['members_rights']


#
# def get_mock_chat():
#     async def get_administrators():
#         return [CHAT_MEMBER.as_object()]
#
#     MYCHAT = DatasetItem(
#         {
#             **CHAT,
#             'type': 'group',
#             'get_administrators': get_administrators,
#         },
#         model=Chat,
#     )
#     return MYCHAT
#
#
# async def test_rights_filter(test_session):
#     cache=Cache()
#
#     cache.write_chat(
#         await chat.create(test_session, id=12345678, members_rights=False)
#     )
#
#     bot = await make_bot(
#         create_trigger,
#         RightsFilter(), StateFilter(None), Command('action_add'),
#         cache=cache,
#     )
#     assert await bot.query(
#         message=MESSAGE.as_object(
#             text='/action_add',
#             chat=get_mock_chat(),
#             from_user=USER,
#         )
#     ) == 'a'

