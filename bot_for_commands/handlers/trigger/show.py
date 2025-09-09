from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot_for_commands.cache import Cache


router = Router()


@router.message(Command(commands=["trigger_show"]))
async def show_triggers(message: Message, cache: Cache):
    answ = '\n'.join([
        f'{word}: {values["answer"]}'
        for word, values in cache.read_chat(message.chat.id)['triggers'].items()
    ])

    await message.answer(f'Слова-триггеры с ответами:\n{answ}')

