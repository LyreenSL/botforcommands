from bot_for_commands.database.models import Chat, Trigger, Action


class ChatNotInCacheError(Exception):
    pass

class TriggerNotInCacheError(Exception):
    pass

class ActionNotInCacheError(Exception):
    pass


class Cache:
    def __init__(self):
        self._cache = {}

    def reload(self, chats_list: list[Chat]) -> None:
        self._cache = {chat.id: self.chat_to_json(chat) for chat in chats_list}

    def read_chat(self, id: int) -> dict:
        try:
            return self._cache[id]
        except KeyError:
            raise ChatNotInCacheError()

    def read_trigger(self, chat_id: int, word: str) -> dict:
        try:
            return self.read_chat(chat_id)['triggers'][word]
        except KeyError:
            raise TriggerNotInCacheError()

    def read_action(self, chat_id: int, command: str) -> dict:
        try:
            return self.read_chat(chat_id)['actions'][command]
        except KeyError:
            raise ActionNotInCacheError()

    def write_chat(self, chat: Chat) -> None:
        self._cache[chat.id] = self.chat_to_json(chat)

    def write_trigger(self, trigger: Trigger) -> None:
        self.read_chat(trigger.chat_id)['triggers'][trigger.word] = self.trigger_to_json(trigger)

    def write_action(self, action: Action) -> None:
        self.read_chat(action.chat_id)['actions'][action.command] = self.action_to_json(action)

    def delete_chat(self, id: int) -> None:
        try:
            del self._cache[id]
        except KeyError:
            raise ChatNotInCacheError()

    def delete_trigger(self, chat_id: int, word: str) -> None:
        try:
            del self.read_chat(chat_id)['triggers'][word]
        except KeyError:
            raise TriggerNotInCacheError()

    def delete_action(self, chat_id: int, command: str) -> None:
        try:
            del self.read_chat(chat_id)['actions'][command]
        except KeyError:
            raise ActionNotInCacheError()

    @classmethod
    def chat_to_json(cls, chat: Chat) -> dict:
        return {
            'members_rights': chat.members_rights,
            'welcome_message': chat.welcome_message,
            'triggers': {trigger.word: cls.trigger_to_json(trigger) for trigger in chat.triggers},
            'actions': {action.command: cls.action_to_json(action) for action in chat.actions},
        }

    @classmethod
    def trigger_to_json(cls, trigger: Trigger) -> dict:
        return {
            'id': trigger.id,
            'answer': trigger.answer,
        }

    @classmethod
    def action_to_json(cls, action: Action) -> dict:
        return {
            'id': action.id,
            'is_interaction': action.is_interaction,
            'text': action.text,
        }

    @classmethod
    def json_to_chat(cls, json: dict, chat_id: int) -> Chat:
        return Chat(
            id=chat_id, members_rights=json['members_rights'], welcome_message=json['welcome_message'],
            triggers=cls.json_to_triggers(json['triggers'], chat_id=chat_id),
            actions=cls.json_to_actions(json['actions'], chat_id=chat_id),
        )

    @classmethod
    def json_to_triggers(cls, json: dict, chat_id: int) -> list[Trigger]:
        return [
            Trigger(
                word=key, answer=value['answer'], chat_id=chat_id
            )
            for key, value in json.items()
        ]

    @classmethod
    def json_to_actions(cls, json: dict, chat_id: int) -> list[Action]:
        return [
            Action(
                command=key, is_interaction=value['is_interaction'],
                text=value['text'], chat_id=chat_id
            )
            for key, value in json.items()
        ]

