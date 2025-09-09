from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.cache import Cache
from bot_for_commands.database.crud import chat


router = Router()

_filters = (
    F.chat.type.not_in({'group', 'supergroup'}) |
    (F.chat.type.in_({'group', 'supergroup'}) & F.from_user.status.in_({'creator', 'administrator'}))
)


@router.message(_filters, Command(commands=['members_rights_off']))
async def members_rights_off(message: Message, db_session: AsyncSession, cache: Cache):
    await chat.update(db_session, message.chat.id, members_rights=False)
    cache.read_chat(message.chat.id)['members_rights'] = False
    await message.answer('Пользователи лишены права редактирования')


@router.message(_filters, Command(commands=['members_rights_on']))
async def members_rights_on(message: Message, db_session: AsyncSession, cache: Cache):
    await chat.update(db_session, message.chat.id, members_rights=True)
    cache.read_chat(message.chat.id)['members_rights'] = True
    await message.answer('Пользователям даны права редактирования')

