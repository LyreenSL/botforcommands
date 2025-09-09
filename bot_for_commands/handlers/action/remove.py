from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.states import ActionRemoveState
from bot_for_commands.database.crud import action
from bot_for_commands.database.exceptions import ActionDontExistError
from bot_for_commands.cache import Cache, ActionNotInCacheError
from bot_for_commands.filters import RightsFilter


router = Router()


@router.message(RightsFilter(), StateFilter(None), Command(commands=['action_remove']))
async def remove_action(message: Message, state: FSMContext):
    await state.set_state(ActionRemoveState.set_command_for_remove)

    await message.answer('Введите действие')


@router.message(ActionRemoveState.set_command_for_remove, F.text | F.sticker)
async def set_command_for_remove(message: Message, state: FSMContext, db_session: AsyncSession, cache: Cache):

    async def action_delete(command):
        try:
            await action.delete(
                db_session,
                cache.read_action(message.chat.id, command)['id']
            )
            cache.delete_action(message.chat.id, command)
            return f"'{command}' удалено"
        except (ActionNotInCacheError, ActionDontExistError):
            return f"'{command}' не найдено"

    if message.sticker:
        answ = f'\n{await action_delete(message.sticker.file_unique_id)}'

    if message.text:
        answ = '\n'.join([
            await action_delete(command)
            for command in message.text.split(';')
        ])

    await state.clear()
    await message.answer(answ)

