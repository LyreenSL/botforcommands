import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from bot_for_commands.database.crud import chat
from bot_for_commands.database.exceptions import ChatDontExistError
from bot_for_commands.cache import ChatNotInCacheError


class ChatNotInDBMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        try:
            result = await handler(event, data)

        except (ChatDontExistError, ChatNotInCacheError):
            chat_id = event.chat.id if type(event) == Message else event.message.chat.id
            data['cache'].write_chat(
                await chat.create(data['db_session'], id=chat_id)
            )
            result = await handler(event, data)

        except Exception as e:
            # logging.exception(e)
            if data['state']:
                await data['state'].clear()
            if type(event) == Message:
                event.answer('Что-то пошло не так, операция отменена')
            raise e
            # return False

        return result

