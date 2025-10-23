from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Iterable
from app.requests.get.get_datasets import get_datasets
from app.requests.get.get_distributions import get_distributions
from pprint import pprint


task_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Регрессия", callback_data="regression_task")],
        [InlineKeyboardButton(text="Классификация", callback_data="classification_task")],
        [InlineKeyboardButton(text="Кластеризация", callback_data="clusterization_task")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)

