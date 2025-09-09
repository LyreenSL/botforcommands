from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.filters import RightsFilter
from bot_for_commands.cache import Cache
from bot_for_commands.database.crud import chat


router = Router()


@router.message(RightsFilter(), Command(commands=['welcome_remove']))
async def welcome_remove(message: Message, db_session: AsyncSession, cache: Cache):
    chat_info = cache.read_chat(message.chat.id)

    if not chat_info['welcome_message']:
        await message.answer('Нечего удалять')
        return

    await chat.update(db_session, message.chat.id, welcome_message=None)
    chat_info['welcome_message'] = None
    await message.answer('Удалено')

