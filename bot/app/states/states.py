from aiogram.fsm.state import StatesGroup, State


class Distribution(StatesGroup):
    handle_distribution = State()
    handle_edit_distribution = State()
    name = State()
    params = State()
    description = State()
    edit_distribution = State()
    distribution_id = State()


class Dataset(StatesGroup):
    handle_dataset = State()
    handle_edit_dataset = State()
    name = State()
    file = State()


class Send(StatesGroup):
    handle = State()
    message = State()


class File(StatesGroup):
    waiting_for_file = State()
    waiting_for_name = State()
    waiting_for_replace_file = State()

