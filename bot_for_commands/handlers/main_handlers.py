from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


router = Router()


with open('helper.txt', 'r') as f:
    helper = f.read()


@router.message(Command(commands=["help", "start"]))
async def cmd_help(message: Message):
    await message.answer(helper)


@router.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        await message.answer(text="Отменено")
    else:
        await message.answer(text="Нечего отменять")

