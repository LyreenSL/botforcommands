import json
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.types.input_file import BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot_for_commands.states import SetDataState
from bot_for_commands.database.crud import chat
from bot_for_commands.cache import Cache
from bot_for_commands.filters import RightsFilter


router = Router()


@router.message(Command(commands=['data_get']))
async def data_get(message: Message, cache: Cache):

    json_file = bytes(
        json.dumps(cache.read_chat(message.chat.id)),
        encoding='utf-8'
    )
    await message.reply_document(
        BufferedInputFile(json_file, f'{message.chat.id}.json')
    )


@router.message(RightsFilter(), StateFilter(None), Command(commands=['data_set']))
async def data_set(message: Message, state: FSMContext):
    await state.set_state(SetDataState.set_json)

    await message.answer('Отправьте json-файл')


@router.message(F.document, SetDataState.set_json)
async def set_json(message: Message, state: FSMContext, cache: Cache, db_session: AsyncSession, bot: Bot):

    try:
        json_data = json.loads((
            await bot.download(message.document)
        ).read())

        cache.write_chat(
            await chat.replace(
                db_session, 
                id=message.chat.id,
                members_rights=json_data['members_rights'],
                welcome_message=json_data['welcome_message'],
                triggers=Cache.json_to_triggers(json_data['triggers'], message.chat.id),
                actions=Cache.json_to_actions(json_data['actions'], message.chat.id),
            )
        )
    except (KeyError, ValueError):
        await message.answer(
            'Неправильный или повреждённый файл, '
            'отправьте json-файл, полученный от /data_get, '
            'или отмените комманду через /cancel'
        )
        return

    await state.clear()
    await message.answer('Принято')

