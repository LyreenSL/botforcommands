import pytest
from aiogram import F
from aiogram.filters import Command
from aiogram_tests.types.dataset import MESSAGE

from bot_for_commands.handlers.action.create import create_action, set_interaction, set_command, set_text
from bot_for_commands.handlers.action.show import show_actions
from bot_for_commands.handlers.action.remove import remove_action, set_command_for_remove
from bot_for_commands.handlers.answers import actions_answers
from bot_for_commands.filters import ActionsFilter
from bot_for_commands.states import ActionCreateState, ActionRemoveState
from bot_for_commands.cache import ActionNotInCacheError
from bot_for_commands.database.crud import action
from bot_for_commands.tests.test_handlers.common import make_bot


async def test_action_create(test_session, test_cache):
    bot1 = await make_bot(create_action, Command(commands=['action_add']))
    assert (
        await bot1.get_answer(text='/action_add') ==
        'Является ли команда взаимодействием? '
        '(Пишется ли в конце имя пользователя, '
        'на сообщение которого ответили командой?) (да / нет)'
    )
    assert await bot1.get_context().get_state() == ActionCreateState.set_interaction

    bot2 = await make_bot(set_interaction, F.text, state_from_bot=bot1)
    assert await bot2.get_answer(text='aaa') == 'Недопустимое значение (да или нет?)'
    assert await bot2.get_context().get_state() == ActionCreateState.set_interaction
    assert await bot2.get_answer(text='Да') == 'Введите команду'
    assert await bot2.get_context().get_data() == {'is_interaction': True}
    assert await bot2.get_context().get_state() == ActionCreateState.set_command

    bot3 = await make_bot(set_command, F.text, state_from_bot=bot2)
    assert (
        await bot3.get_answer(text='Command1; commaND2 ; ') ==
        'Введите текст команды (желательно с маленькой буквы, '
        'так как предложение будет начинаться с юзернейма)'
    )
    assert await bot3.get_context().get_data() == {
        'is_interaction': True, 'command': 'Command1; commaND2 ; '
    }
    assert await bot3.get_context().get_state() == ActionCreateState.set_text

    bot4 = await make_bot(
        set_text, F.text, state_from_bot=bot3, db_session=test_session, cache=test_cache
    )
    assert await bot4.get_answer(text='text text text') == 'Добавлено'
    assert not await bot4.get_context().get_state()

    action_inst1 = test_cache.read_action(12345678, 'command1')
    action_inst2 = test_cache.read_action(12345678, 'command2')
    with pytest.raises(ActionNotInCacheError):
        test_cache.read_action(12345678, '')
    assert (
        await action.get(test_session, action_inst1['id'])
    ).command == 'command1'
    assert (
        await action.get(test_session, action_inst2['id'])
    ).command == 'command2'


async def test_action_create_duplicate(test_session, test_cache):
    await test_action_create(test_session, test_cache)
    await test_action_create(test_session, test_cache)


async def test_action_show(test_session, test_cache):
    await test_action_create(test_session, test_cache)

    bot = await make_bot(show_actions, Command(commands=['action_show']), cache=test_cache)
    assert (
        await bot.get_answer(text='/action_show') ==
        'Список комманд:\ncommand1 (взаимодействие): text text text\ncommand2 (взаимодействие): text text text'
    )

async def test_action_delete(test_session, test_cache):
    await test_action_create(test_session, test_cache)

    bot1 = await make_bot(remove_action, Command(commands=['action_remove']))
    assert await bot1.get_answer(text='/action_remove') == 'Введите действие'
    assert await bot1.get_context().get_state() == ActionRemoveState.set_command_for_remove

    bot2 = await make_bot(
        set_command_for_remove, F.text, state_from_bot=bot1, cache=test_cache, db_session=test_session
    )
    assert (
        await bot2.get_answer(text='command1;command2;aaa') ==
        "'command1' удалено\n'command2' удалено\n'aaa' не найдено"
    )
    assert not await bot2.get_context().get_state()

    with pytest.raises(ActionNotInCacheError):
        test_cache.read_action(12345678, 'command1')
    with pytest.raises(ActionNotInCacheError):
        test_cache.read_action(12345678, 'command2')


async def test_action_answer(test_session, test_cache):
    await test_action_create(test_session, test_cache)

    bot_answer = await make_bot(actions_answers, ActionsFilter(), cache=test_cache)
    assert (
        await bot_answer.get_answer(text='command1', reply_to_message=MESSAGE.as_object()) ==
        '[FirstName LastName](tg://user?id=12345678) text text text [FirstName LastName](tg://user?id=12345678)'
    )

