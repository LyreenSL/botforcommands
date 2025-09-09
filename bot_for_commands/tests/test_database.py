import pytest

from bot_for_commands.database.models import Trigger, Action
from bot_for_commands.database.crud import action, chat, trigger
from bot_for_commands.database.exceptions import (
    ChatDontExistError, TriggerDontExistError, ActionDontExistError,
    ChatDuplicateError, TriggerDuplicateError, ActionDuplicateError,
)
from bot_for_commands.tests.inputs import (
    chat_create_input, trigger_create_input, action_create_input,
    chat_update_input, trigger_update_input, action_update_input,
)


def attrs_are_equal(input, inst):
    for key, value in input.items():
        assert value == getattr(inst, key)

async def chat_create(session):
    return await chat.create(session=session, **chat_create_input)

async def trigger_create(session):
    return await trigger.create(session=session, **trigger_create_input)

async def action_create(session):
    return await action.create(session=session, **action_create_input)


async def test_chat_create(test_session):
    attrs_are_equal(chat_create_input, await chat_create(test_session))

async def test_trigger_create(test_session):
    await test_chat_create(test_session)
    attrs_are_equal(trigger_create_input, await trigger_create(test_session))

async def test_action_create(test_session):
    await test_chat_create(test_session)
    attrs_are_equal(action_create_input, await action_create(test_session))


async def test_trigger_create_for_non_exist_chat(test_session):
    with pytest.raises(ChatDontExistError):
        await trigger_create(test_session)

async def test_action_create_for_non_exist_chat(test_session):
    with pytest.raises(ChatDontExistError):
        await action_create(test_session)


async def test_chat_create_duplicate(test_session):
    await chat_create(test_session)
    with pytest.raises(ChatDuplicateError):
        await chat_create(test_session)

async def test_trigger_create_duplicate(test_session):
    await chat_create(test_session)
    await trigger_create(test_session)
    with pytest.raises(TriggerDuplicateError):
        await trigger_create(test_session)

async def test_action_create_duplicate(test_session):
    await chat_create(test_session)
    await action_create(test_session)
    with pytest.raises(ActionDuplicateError):
        await action_create(test_session)


async def test_chat_get(test_session):
    chat_inst = await chat_create(test_session)
    attrs_are_equal(
        chat_create_input,
        await chat.get(session=test_session, id=chat_inst.id),
    )

async def test_trigger_get(test_session):
    await chat_create(test_session)
    trigger_inst = await trigger_create(test_session)
    attrs_are_equal(
        trigger_create_input,
        await trigger.get(session=test_session, id=trigger_inst.id),
    )

async def test_action_get(test_session):
    await chat_create(test_session)
    action_inst = await action_create(test_session)
    attrs_are_equal(
        action_create_input,
        await action.get(session=test_session, id=action_inst.id),
    )


async def test_get_all(test_session):
    await chat_create(test_session)
    await trigger_create(test_session)
    await action_create(test_session)
    await chat.create(session=test_session, id=456456)

    all_instances = await chat.get_all(session=test_session)
    attrs_are_equal(chat_create_input, all_instances[0])
    attrs_are_equal({'id': 456456, 'members_rights': True}, all_instances[1])
    attrs_are_equal(trigger_create_input, all_instances[0].triggers[0])
    attrs_are_equal(action_create_input, all_instances[0].actions[0])


async def test_chat_update(test_session):
    chat_inst = await chat_create(test_session)
    chat_inst = await chat.update(session=test_session, id=chat_inst.id, **chat_update_input)
    attrs_are_equal(chat_update_input, chat_inst)
    assert (
        chat_create_input['id'] == chat_inst.id and
        chat_create_input['members_rights'] != chat_inst.members_rights
    )

async def test_trigger_update(test_session):
    await chat_create(test_session)
    trigger_inst = await trigger_create(test_session)
    trigger_inst = await trigger.update(session=test_session, id=trigger_inst.id, **trigger_update_input)
    attrs_are_equal(trigger_update_input, trigger_inst)
    assert (
        trigger_create_input['word'] != trigger_inst.word and
        trigger_create_input['answer'] != trigger_inst.answer
    )

async def test_action_update(test_session):
    await chat_create(test_session)
    action_inst = await action_create(test_session)
    action_inst = await action.update(session=test_session, id=action_inst.id, **action_update_input)
    attrs_are_equal(action_update_input, action_inst)
    assert (
        action_create_input['is_interaction'] != action_inst.is_interaction and
        action_create_input['command'] == action_inst.command and
        action_create_input['text'] != action_inst.text
    )


async def test_chat_update_non_exist(test_session):
    with pytest.raises(ChatDontExistError):
        await chat.update(session=test_session, id=-14, **chat_update_input)

async def test_trigger_update_non_exist(test_session):
    with pytest.raises(TriggerDontExistError):
        await trigger.update(session=test_session, id=-14, **trigger_update_input)

async def test_action_update_non_exist(test_session):
    with pytest.raises(ActionDontExistError):
        await action.update(session=test_session, id=-14, **action_update_input)


async def test_chat_delete(test_session):
    chat_inst = await chat_create(test_session)
    trigger_inst = await trigger_create(test_session)
    action_inst = await action_create(test_session)
    await chat.delete(session=test_session, id=chat_inst.id)
    assert not await chat.get(session=test_session, id=action_inst.id)
    assert not await trigger.get(session=test_session, id=trigger_inst.id)
    assert not await action.get(session=test_session, id=action_inst.id)

async def test_trigger_delete(test_session):
    await chat_create(test_session)
    trigger_inst = await trigger_create(test_session)
    await trigger.delete(session=test_session, id=trigger_inst.id)
    assert not await trigger.get(session=test_session, id=trigger_inst.id)

async def test_action_delete(test_session):
    await chat_create(test_session)
    action_inst = await action_create(test_session)
    await action.delete(session=test_session, id=action_inst.id)
    assert not await action.get(session=test_session, id=action_inst.id)


async def test_chat_delete_non_exist(test_session):
    with pytest.raises(ChatDontExistError):
        await chat.delete(session=test_session, id=-14)

async def test_trigger_delete_non_exist(test_session):
    with pytest.raises(TriggerDontExistError):
        await trigger.delete(session=test_session, id=-14)

async def test_action_delete_non_exist(test_session):
    with pytest.raises(ActionDontExistError):
        await action.delete(session=test_session, id=-14)


async def test_chat_replace(test_session):
    await chat_create(test_session)
    await trigger_create(test_session)
    await action_create(test_session)
    await chat.replace(
        session=test_session, **chat_create_input,
        triggers=[Trigger(**trigger_create_input)],
        actions=[Action(**action_create_input)],
    )

async def test_chat_replace_non_exist(test_session):
    with pytest.raises(ChatDontExistError):
        await chat.replace(
            session=test_session, **chat_create_input,
            triggers=[], actions=[],
        )

