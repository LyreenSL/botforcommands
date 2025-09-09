import pytest
from aiogram import F
from aiogram.filters import Command

from bot_for_commands.handlers.trigger.create import create_trigger, set_word, set_answer
from bot_for_commands.handlers.trigger.show import show_triggers
from bot_for_commands.handlers.trigger.remove import remove_trigger, set_word_for_remove
from bot_for_commands.handlers.answers import triggers_answers
from bot_for_commands.filters import TriggersFilter
from bot_for_commands.states import TriggerCreateState, TriggerRemoveState
from bot_for_commands.cache import TriggerNotInCacheError
from bot_for_commands.database.crud import trigger
from bot_for_commands.tests.test_handlers.common import make_bot


async def test_trigger_create(test_session, test_cache):
    bot1 = await make_bot(create_trigger, Command(commands=['trigger_add']))
    assert await bot1.get_answer(text='/trigger_add') == 'Введите слово-триггер'
    assert await bot1.get_context().get_state() == TriggerCreateState.set_word

    bot2 = await make_bot(set_word, F.text, state_from_bot=bot1)
    assert await bot2.get_answer(text=' woRD1 ;Word2 ; ') == 'Введите ответ'
    assert await bot2.get_context().get_data() == {'word': ' woRD1 ;Word2 ; '}
    assert await bot2.get_context().get_state() == TriggerCreateState.set_answer

    bot3 = await make_bot(set_answer, F.text, state_from_bot=bot2, db_session=test_session, cache=test_cache)
    assert await bot3.get_answer(text='Answer answer answer') == 'Добавлено'
    assert not await bot3.get_context().get_state()

    trigger_inst1 = test_cache.read_trigger(12345678, 'word1')
    trigger_inst2 = test_cache.read_trigger(12345678, 'word2')
    with pytest.raises(TriggerNotInCacheError):
        test_cache.read_trigger(12345678, '')
    assert (
        await trigger.get(test_session, trigger_inst1['id'])
    ).word == 'word1'
    assert (
        await trigger.get(test_session, trigger_inst2['id'])
    ).word == 'word2'


async def test_trigger_create_duplicate(test_session, test_cache):
    await test_trigger_create(test_session, test_cache)
    await test_trigger_create(test_session, test_cache)


async def test_trigger_show(test_session, test_cache):
    await test_trigger_create(test_session, test_cache)
    bot = await make_bot(show_triggers, Command(commands=['trigger_show']), cache=test_cache)
    assert (
        await bot.get_answer(text='/trigger_show') ==
        'Слова-триггеры с ответами:\nword1: Answer answer answer\nword2: Answer answer answer'
    )


async def test_trigger_delete(test_session, test_cache):
    await test_trigger_create(test_session, test_cache)
    bot1 = await make_bot(remove_trigger, Command(commands=['trigger_remove']))
    assert (
        await bot1.get_answer(text='/trigger_remove') ==
        'Введите слово-триггер'
    )
    assert await bot1.get_context().get_state() == TriggerRemoveState.set_word_for_remove

    bot2 = await make_bot(
        set_word_for_remove, F.text, state_from_bot=bot1, cache=test_cache, db_session=test_session
    )
    assert (
        await bot2.get_answer(text='word1;word2;aaa') ==
        "'word1' удалено\n'word2' удалено\n'aaa' не найдено"
    )
    assert not await bot2.get_context().get_state()

    with pytest.raises(TriggerNotInCacheError):
        test_cache.read_trigger(12345678, 'word1')
    with pytest.raises(TriggerNotInCacheError):
        test_cache.read_trigger(12345678, 'word2')


async def test_trigger_answer(test_session, test_cache):
    await test_trigger_create(test_session, test_cache)
    bot_answer = await make_bot(triggers_answers, TriggersFilter(), cache=test_cache)
    assert await bot_answer.get_answer(text='aasdf wefwsdvc word1 asfsf') == 'Answer answer answer'

