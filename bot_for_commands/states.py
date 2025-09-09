from aiogram.fsm.state import StatesGroup, State


class TriggerCreateState(StatesGroup):
    set_word = State()
    set_answer = State()


class TriggerRemoveState(StatesGroup):
    set_word_for_remove = State()


class ActionCreateState(StatesGroup):
    set_interaction = State()
    set_command = State()
    set_text = State()


class ActionRemoveState(StatesGroup):
    set_command_for_remove = State()


class SetDataState(StatesGroup):
    set_json = State()


class SetWelcomeState(StatesGroup):
    set_welcome = State()

