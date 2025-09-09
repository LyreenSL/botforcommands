from aiogram import Router
from aiogram.types import Message

from bot_for_commands.filters import TriggersFilter, ActionsFilter
from bot_for_commands.cache import Cache


router = Router()


@router.message(ActionsFilter())
async def actions_answers(message: Message, cache: Cache, action_answer: str):
    await message.answer(action_answer, parse_mode='Markdown')


@router.message(TriggersFilter())
async def triggers_answers(message: Message, cache: Cache, trigger_answer: str):
    await message.reply(trigger_answer, parse_mode='Markdown')

