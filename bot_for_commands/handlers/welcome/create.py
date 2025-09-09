from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.filters import RightsFilter
from bot_for_commands.states import SetWelcomeState
from bot_for_commands.cache import Cache
from bot_for_commands.database.crud import chat


router = Router()


@router.message(RightsFilter(), StateFilter(None), Command(commands=['welcome_add']))
async def welcome_add(message: Message, state: FSMContext):
    await state.set_state(SetWelcomeState.set_welcome)

    await message.answer(
        'Введите приветственное сообщение'
    )


@router.message(
    F.photo | F.video | F.sticker  | F.animation | F.text,
    RightsFilter(), StateFilter(SetWelcomeState.set_welcome),
)
async def set_welcome(message: Message, state: FSMContext, db_session: AsyncSession, cache: Cache):
    if message.photo:
        welcome_message = f'pht:{message.photo[0].file_id};{message.caption}'
    elif message.video:
        welcome_message = f'vid:{message.video.file_id};{message.caption}'
    elif message.sticker:
        welcome_message = f'stk:{message.sticker.file_id}'
    elif message.animation:
        welcome_message = f'gif:{message.animation.file_id}'
    else:
        welcome_message = f'txt:{message.text}'

    await chat.update(db_session, message.chat.id, welcome_message=welcome_message)
    cache.read_chat(message.chat.id)['welcome_message'] = welcome_message

    await state.clear()
    await message.answer('Добавлено')

