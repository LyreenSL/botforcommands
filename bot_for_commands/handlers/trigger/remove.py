from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.states import TriggerRemoveState
from bot_for_commands.database.crud import trigger
from bot_for_commands.database.exceptions import TriggerDontExistError
from bot_for_commands.cache import Cache, TriggerNotInCacheError
from bot_for_commands.filters import RightsFilter


router = Router()


@router.message(RightsFilter(), StateFilter(None), Command(commands=['trigger_remove']))
async def remove_trigger(message: Message, state: FSMContext):
    await state.set_state(TriggerRemoveState.set_word_for_remove)

    await message.answer('Введите слово-триггер')


@router.message(TriggerRemoveState.set_word_for_remove, F.text)
async def set_word_for_remove(message: Message, state: FSMContext, db_session: AsyncSession, cache: Cache):

    async def trigger_delete(word):
        try:
            await trigger.delete(
                db_session,
                cache.read_trigger(message.chat.id, word)['id']
            )
            cache.delete_trigger(message.chat.id, word)
            return f"'{word}' удалено"
        except (TriggerNotInCacheError, TriggerDontExistError):
            return f"'{word}' не найдено"

    answ = '\n'.join([
        await trigger_delete(word.lower().strip())
        for word in message.text.split(';')
    ])

    await state.clear()
    await message.answer(answ)

