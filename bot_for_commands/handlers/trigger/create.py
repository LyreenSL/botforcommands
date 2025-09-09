from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.states import TriggerCreateState
from bot_for_commands.database.crud import trigger
from bot_for_commands.database.exceptions import ChatDontExistError, TriggerDuplicateError
from bot_for_commands.cache import Cache
from bot_for_commands.filters import RightsFilter


router = Router()


@router.message(RightsFilter(), StateFilter(None), Command(commands=['trigger_add']))
async def create_trigger(message: Message, state: FSMContext):
    await state.set_state(TriggerCreateState.set_word)

    await message.answer(
        'Введите слово-триггер'
    )


@router.message(TriggerCreateState.set_word, F.text)
async def set_word(message: Message, state: FSMContext):
    await state.update_data(word=message.text)
    await state.set_state(TriggerCreateState.set_answer)

    await message.answer('Введите ответ')


@router.message(TriggerCreateState.set_answer, F.text)
async def set_answer(message: Message, state: FSMContext, db_session: AsyncSession, cache: Cache):

    for word in (await state.get_data())['word'].split(';'):

        if not word.lower().strip():
            continue
            
        try:
            cache.write_trigger(
                await trigger.create(
                    db_session,
                    word=word.lower().strip(),
                    answer=message.text,
                    chat_id=message.chat.id,
                )
            )

        except TriggerDuplicateError:
            trigger_inst = cache.read_trigger(
                message.chat.id,
                word.lower().strip(),
            )
            cache.write_trigger(
                await trigger.update(
                    db_session,
                    id=trigger_inst['id'],
                    answer=message.text,
                )
            )

    await state.clear()
    await message.answer('Добавлено')

