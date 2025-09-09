import re
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot_for_commands.cache import Cache, ActionNotInCacheError


def get_mention(message):
    return f'[{message.from_user.full_name}](tg://user?id={message.from_user.id})'


class TriggersFilter(BaseFilter):
    async def __call__(self, message: Message, cache: Cache):

        mes = message.caption if message.caption else message.text
        if not mes:
            return False

        for word, values in cache.read_chat(message.chat.id)['triggers'].items():
            if re.search(fr"(^|\W){word}($|\W)", mes.lower(), re.IGNORECASE):
                return {'trigger_answer': values['answer']}

        return False


class ActionsFilter(BaseFilter):
    async def __call__(self, message: Message, cache: Cache):

        if message.sticker:
            try:
                action = cache.read_action(message.chat.id, message.sticker.file_unique_id)
                return {
                    'action_answer': (
                        f'{get_mention(message)} {action["text"]} '
                        f'{get_mention(message.reply_to_message) if action["interaction"] else ""}'
                    )
                }
            except ActionNotInCacheError:
                return False

        mes = message.caption if message.caption else message.text
        if mes:
            for command, values in cache.read_chat(message.chat.id)['actions'].items():
                if mes.lower().startswith(command):
                    return {
                        'action_answer': (
                            f'{get_mention(message)} {values["text"]} '
                            f'{get_mention(message.reply_to_message) if values["is_interaction"] else ""}  '
                            f'{mes[len(command):]}'
                        ).strip()
                    }
            return False

        return False


class RightsFilter(BaseFilter):
    async def __call__(self, message: Message, cache: Cache):
        if message.chat.type not in {'group', 'supergroup'}:
            return True

        if cache.read_chat(message.chat.id)['members_rights']:
            return True

        if message.from_user in [
            admin.user for admin in await message.chat.get_administrators()
        ]:
            return True

        await message.answer('У вас нет прав на редактирование')
        return False

