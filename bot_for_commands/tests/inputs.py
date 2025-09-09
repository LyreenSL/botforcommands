from bot_for_commands.database.models import Chat, Trigger, Action


chat_create_input = {'id': 123123, 'members_rights': True}
trigger_create_input = {'word': 'word1', 'answer': 'answer1', 'chat_id': 123123}
action_create_input = {'is_interaction': True, 'command': 'command1', 'text': 'text1', 'chat_id': 123123}

chat_update_input = {'members_rights': False}
trigger_update_input = {'word': 'word2word2', 'answer': '4answer4'}
action_update_input = {'is_interaction': False, 'text': 'textxtxt'}

inst_list = [
    Chat(id = 234234, members_rights = True, welcome_message = 'hello', triggers=[
        Trigger(id=1, word = 'aaa', answer = 'aaaaa', chat_id = 234234)
    ], actions=[
        Action(id=1, is_interaction = True, command = 'bbb', text = 'abababa', chat_id = 678678)
    ]),
    Chat(id = 678678, members_rights = False, welcome_message = 'hello2', triggers=[], actions=[]),
]

inst_json = {
        234234: {'members_rights': True, 'welcome_message': 'hello', 'triggers': {
            'aaa': {'id': 1, 'answer': 'aaaaa'}
        }, 'actions': {
            'bbb': {'id': 1, 'is_interaction': True, 'text': 'abababa'}
        }},
        678678: {'members_rights': False, 'welcome_message': 'hello2', 'triggers': {}, 'actions': {}}
    }

