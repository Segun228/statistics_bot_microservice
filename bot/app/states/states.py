from aiogram.fsm.state import StatesGroup, State

class Send(StatesGroup):
    handle = State()
    message = State()

class Distribution(StatesGroup):
    handle_distribution = State()
    handle_edit_distribution = State()
    name = State()
    distribution_type = State()
    params = State()
    description = State()
    edit_distribution = State()
    distribution_id = State()

class DistributionEdit(StatesGroup):
    handle_distribution = State()
    handle_edit_distribution = State()
    name = State()
    distribution_type = State()
    params = State()
    description = State()
    edit_distribution = State()
    distribution_id = State()

class Dataset(StatesGroup):
    handle_dataset = State()
    handle_edit_dataset = State()
    name = State()
    file = State()


class DatasetEdit(StatesGroup):
    handle_dataset = State()
    handle_edit_dataset = State()
    name = State()
    file = State()


class Probability(StatesGroup):
    probability = State()


class Interval(StatesGroup):
    interval = State()


class Sample(StatesGroup):
    sample = State()


class Quantile(StatesGroup):
    quantile = State()


class Percentile(StatesGroup):
    percentile = State()

class File(StatesGroup):
    waiting_for_file = State()
    waiting_for_name = State()
    waiting_for_replace_file = State()


class Errors(StatesGroup):
    handle_errors = State()
    alpha = State()


class Groups(StatesGroup):
    handle = State()
    test = State()
    controle = State()


class SampleSize(StatesGroup):
    mde = State()


class Confirm(StatesGroup):
    bundle = State()
    confirmed = State()
