import pytest

from bot_for_commands.database.models import Chat, Trigger, Action
from bot_for_commands.cache import Cache
from bot_for_commands.cache import ChatNotInCacheError, TriggerNotInCacheError, ActionNotInCacheError
from bot_for_commands.tests.inputs import (
    chat_create_input, trigger_create_input, action_create_input,
    inst_list, inst_json
)


def write_chat(cache):
    cache.write_chat(Chat(**chat_create_input))

def write_trigger(cache):
    cache.write_trigger(Trigger(**trigger_create_input))

def write_action(cache):
    cache.write_action(Action(**action_create_input))

def read_chat(cache):
    return cache.read_chat(chat_create_input['id'])

def read_trigger(cache):
    return cache.read_trigger(
        trigger_create_input['chat_id'],
        trigger_create_input['word'],
    )

def read_action(cache):
    return cache.read_action(
        action_create_input['chat_id'],
        action_create_input['command'],
    )

def vars_exclude_adapter(obj):
    return {**vars(obj), '_sa_adapter': None}


def test_reload(test_cache):
    test_cache.reload(inst_list)
    assert test_cache._cache == inst_json


def test_chat_write(test_cache):
    write_chat(test_cache)

def test_trigger_write(test_cache):
    write_chat(test_cache)
    write_trigger(test_cache)

def test_action_write(test_cache):
    write_chat(test_cache)
    write_action(test_cache)


def test_trigger_write_without_chat(test_cache):
    with pytest.raises(ChatNotInCacheError):
        write_trigger(test_cache)

def test_action_write_without_chat(test_cache):
    with pytest.raises(ChatNotInCacheError):
        write_action(test_cache)


def test_chat_read(test_cache):
    write_chat(test_cache)
    assert read_chat(test_cache)['members_rights'] == chat_create_input['members_rights']

def test_trigger_read(test_cache):
    write_chat(test_cache)
    write_trigger(test_cache)
    assert read_trigger(test_cache)['answer'] == trigger_create_input['answer']

def test_action_read(test_cache):
    write_chat(test_cache)
    write_action(test_cache)
    assert read_action(test_cache)['text'] == action_create_input['text']
    assert read_action(test_cache)['is_interaction'] == action_create_input['is_interaction']


def test_chat_delete(test_cache):
    write_chat(test_cache)
    test_cache.delete_chat(chat_create_input['id'])
    with pytest.raises(ChatNotInCacheError):
        assert read_chat(test_cache)

def test_trigger_delete(test_cache):
    write_chat(test_cache)
    write_trigger(test_cache)
    
    test_cache.delete_trigger(
        trigger_create_input['chat_id'],
        trigger_create_input['word'],
    )
    with pytest.raises(TriggerNotInCacheError):
        test_cache.read_trigger(chat_create_input['id'], trigger_create_input['word'])

def test_action_delete(test_cache):
    write_chat(test_cache)
    write_action(test_cache)
    test_cache.delete_action(
        action_create_input['chat_id'],
        action_create_input['command'],
    )
    with pytest.raises(ActionNotInCacheError):
        test_cache.read_action(chat_create_input['id'], action_create_input['command'])


def test_cache_update(test_cache):
    write_chat(test_cache)
    read_chat(test_cache)['members_rights'] = False
    assert not read_chat(test_cache)['members_rights']
    write_chat(test_cache)
    assert read_chat(test_cache)['members_rights']


def test_json_to_chat():
    from_json = Cache.json_to_chat(inst_json[234234], 234234)
    from_list = inst_list[0]
    assert from_json.id == from_list.id
    assert from_json.members_rights == from_list.members_rights
    assert from_json.welcome_message == from_list.welcome_message
    assert vars_exclude_adapter(from_json.triggers) == vars_exclude_adapter(from_list.triggers)
    assert vars_exclude_adapter(from_json.actions) == vars_exclude_adapter(from_list.actions)

