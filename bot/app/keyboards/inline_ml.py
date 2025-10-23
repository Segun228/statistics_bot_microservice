from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Iterable
from app.requests.get.get_datasets import get_datasets
from app.requests.get.get_distributions import get_distributions
from pprint import pprint


task_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Регрессия", callback_data="task_regression")],
        [InlineKeyboardButton(text="Классификация", callback_data="task_classification")],
        [InlineKeyboardButton(text="Кластеризация", callback_data="task_clusterization")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)

def list_ml_models(data, task):
    keyboard = InlineKeyboardBuilder()
    data = [] if data is None or not data else data
    for model in data:
        keyboard.add(InlineKeyboardButton(text=f"{model.get('name', "Неизвестная модель")}", callback_data=f"MLmodel_{model.get('id')}"))
    keyboard.add(InlineKeyboardButton(text="Создать модель ✨", callback_data=f"create_ML_model_{task}"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return keyboard.adjust(1).as_markup()


def single_model_menu(
    model,
    model_id
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Предсказать", callback_data=f"model_predict_{model_id}"))
    keyboard.add(InlineKeyboardButton(text="Дообучить", callback_data=f"model_train_{model_id}"))
    keyboard.add(InlineKeyboardButton(text="Обучить заново", callback_data=f"model_retrain_{model_id}"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return keyboard.adjust(1).as_markup()