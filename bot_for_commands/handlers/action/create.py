from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.states import ActionCreateState
from bot_for_commands.database.crud import action
from bot_for_commands.database.exceptions import ChatDontExistError, ActionDuplicateError
from bot_for_commands.cache import Cache
from bot_for_commands.filters import RightsFilter


router = Router()


@router.message(RightsFilter(), StateFilter(None), Command(commands=['action_add']))
async def create_action(message: Message, state: FSMContext):
    await state.set_state(ActionCreateState.set_interaction)

    await message.answer(
        'Является ли команда взаимодействием? '
        '(Пишется ли в конце имя пользователя, '
        'на сообщение которого ответили командой?) (да / нет)'
    )


@router.message(ActionCreateState.set_interaction, F.text)
async def set_interaction(message: Message, state: FSMContext):
    if message.text.lower() not in {'да', 'нет'}:
        await message.answer('Недопустимое значение (да или нет?)')
        return

    await state.update_data(
        is_interaction = True if message.text.lower() == 'да' else False
    )
    await state.set_state(ActionCreateState.set_command)
    await message.answer('Введите команду')


@router.message(ActionCreateState.set_command, F.text | F.sticker)
async def set_command(message: Message, state: FSMContext):

    if message.sticker:
        await state.update_data(command=message.sticker.file_unique_id)

    if message.text:
        await state.update_data(command=message.text)

    await state.set_state(ActionCreateState.set_text)
    await message.answer(
        'Введите текст команды (желательно с маленькой буквы, '
        'так как предложение будет начинаться с юзернейма)'
    )


@router.message(ActionCreateState.set_text, F.text)
async def set_text(message: Message, state: FSMContext, db_session: AsyncSession, cache: Cache):

    interaction = (await state.get_data())['is_interaction']
    for command in (await state.get_data())['command'].split(';'):
        if not command.strip().lower():
            continue

        try:
            cache.write_action(
                await action.create(
                    db_session,
                    is_interaction=interaction,
                    command=command.strip().lower(),
                    text=message.text,
                    chat_id=message.chat.id,
                )
            )

        except ActionDuplicateError:
            action_inst = cache.read_action(
                message.chat.id,
                command.strip().lower(),
            )
            cache.write_action(
                await action.update(
                    db_session,
                    id=action_inst['id'],
                    is_interaction=interaction,
                    command=command.strip().lower(),
                    text=message.text,
                )
            )

    await state.clear()
    await message.answer('Добавлено')

