from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot_for_commands.cache import Cache


router = Router()


@router.message(Command(commands=["action_show"]))
async def show_actions(message: Message, cache: Cache):
    answ = '\n'.join(
        f"{command} {'(взаимодействие)' if values['is_interaction'] else ''}: {values['text']}"
        for command, values in cache.read_chat(message.chat.id)['actions'].items()
    )
    await message.answer(f'Список комманд:\n{answ}')

