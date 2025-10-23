from app.handlers.router import ml_router as router
import logging
import re
import zipfile
import io
import json
import re
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram import F
from typing import Dict, Any
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot
from aiogram.exceptions import TelegramAPIError
from io import BytesIO
import asyncio

from aiogram.types import InputFile

from app.keyboards import inline_user as inline_user_keyboards

from app.keyboards import inline_ml as inline_keyboards

from app.states.states import Errors, Groups, Confirm, Bootstrap, Cuped, Cupac

import pandas as pd
import numpy as np


from app.keyboards.inline_user import  get_distributions_catalogue

from app.filters.IsAdmin import IsAdmin

from app.requests.user.login import login
from app.requests.helpers.get_cat_error import get_cat_error_async

from app.requests.helpers.get_cat_error import get_cat_error_async

from app.requests.user.get_alive import get_alive
from app.requests.user.make_admin import make_admin

from app.kafka.utils import build_log_message

from app.requests.get.get_datasets import get_datasets, retrieve_dataset
from app.requests.get.get_distributions import get_distributions, retrieve_distribution

from app.requests.post.post_dataset import post_dataset
from app.requests.post.post_distribution import post_distribution

from app.requests.put.put_dataset import put_dataset
from app.requests.put.put_distribution import put_distribution

from app.requests.delete.delete_dataset import delete_dataset
from app.requests.delete.deleteDistribution import delete_distribution

from app.requests.dataset.patch_errors.patch_errors import patch_errors
from app.requests.dataset.patch_categories.patch_groups import set_groups

from app.keyboards.reply_dataset import create_reply_column_keyboard_group
from app.states.states import SampleSize


from app.requests.dataset import stats_handlers
from math import floor, ceil


def escape_md(text: str) -> str:
    """Экранирование специальных символов для MarkdownV2"""
    if not text:
        return ""
    
    escape_chars = '_*[]()~`>#+-=|{}.!'
    result = []
    for char in str(text):
        if char in escape_chars:
            result.append(f'\\{char}')
        else:
            result.append(char)
    return ''.join(result)

#===========================================================================================================================
# Меню
#===========================================================================================================================



@router.callback_query(F.data.startswith("ml_models"))
async def get_ml_task_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer(
            "Вы в меню создания моделей машинного обучения\nКакую задачу вы хотите решать?",
            reply_markup=inline_keyboards.task_choice
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)



@router.callback_query(F.data.startswith("regression_task"))
async def get_regression_models_menu(callback: CallbackQuery, state: FSMContext):
    try:
        callback.message.answer("Выберите существующую модель регрессии или создайте новую")
        pass
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("classification_task"))
async def get_classification_models_menu(callback: CallbackQuery, state: FSMContext):
    try:
        callback.message.answer("Выберите существующую модель классификации или создайте новую")
        pass
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("clusterization_task"))
async def get_clusterization_models_menu(callback: CallbackQuery, state: FSMContext):
    try:
        callback.message.answer("Выберите существующую модель кластеризации или создайте новую")
        pass
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)

