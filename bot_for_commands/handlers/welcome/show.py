from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from bot_for_commands.cache import Cache


router = Router()


async def welcome_show(message: Message, cache: Cache):
    welcome_message = cache.read_chat(message.chat.id)['welcome_message']

    if not welcome_message:
        if message.text:
            await message.answer('Ничего нет')
            return
        else:
            return

    match welcome_message[:3]:
        case 'pht':
            media_id, caption = welcome_message[4:].split(';', maxsplit=1)
            await message.answer_photo(media_id, caption=caption)
        case 'vid':
            media_id, caption = welcome_message[4:].split(';', maxsplit=1)
            await message.answer_video(media_id, caption=caption)
        case 'stk':
            await message.answer_sticker(welcome_message[4:])
        case 'gif':
            await message.answer_animation(welcome_message[4:])
        case 'txt':
            await message.answer(welcome_message[4:])


@router.message(F.new_chat_members)
async def welcome_show_new_member(message: Message, cache: Cache):
    return await welcome_show(message, cache)


@router.message(Command(commands=['welcome_show']))
async def welcome_show_command(message: Message, cache: Cache):
    return await welcome_show(message, cache)

