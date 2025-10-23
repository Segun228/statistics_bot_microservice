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
from app.requests.ml_models.get_all_models import get_all_models, retrieve_model
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



@router.callback_query(F.data.startswith("task_"))
async def get_regression_models_menu(callback: CallbackQuery, state: FSMContext):
    try:
        task_type = callback.data.split("_")[1].strip()
        models = await get_all_models(
            telegram_id=callback.from_user.id,
            model_task=task_type
        )
        await callback.message.answer(
            "Выберите существующую модель или создайте новую",
            reply_markup= inline_keyboards.list_ml_models(
                models,
                task = task_type
            )
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("MLmodel_"))
async def retrieve_model_menu(callback: CallbackQuery, state: FSMContext):
    try:
        model_id = int(callback.data.split("_")[1].strip())
        model = await retrieve_model(
            telegram_id=callback.from_user.id,
            model_id=model_id
        )
        if not model:
            raise Exception("Error while retrieving the model")
        
        message_text = format_model_info(model)
        
        await callback.message.answer(
            message_text,
            reply_markup=inline_keyboards.single_model_menu(
                model=model,
                model_id=model_id
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


def format_model_info(model) -> str:
    """Форматирует информацию о модели в красивый текст"""

    emoji = {
        "name": "🏷️",
        "description": "📝", 
        "task": "🎯",
        "type": "🔧",
        "features": "📊",
        "target": "🎯",
        "dates": "📅",
        "urls": "🔗"
    }
    
    created = model.created_at.strftime("%d.%m.%Y %H:%M") if model.created_at else "Не указано"
    updated = model.updated_at.strftime("%d.%m.%Y %H:%M") if model.updated_at else "Не указано"

    features_text = format_features(model.features)
    
    message = f"""
<b>🤖 МАШИННОЕ ОБУЧЕНИЕ | МОДЕЛЬ</b>

{emoji['name']} <b>Название:</b> <code>{model.name or 'Не указано'}</code>

{emoji['description']} <b>Описание:</b>
{model.description or 'Не указано'}

{emoji['task']} <b>Задача:</b> <code>{model.task_display or model.task or 'Не указано'}</code>

{emoji['type']} <b>Тип модели:</b> <code>{model.type_display or model.type or 'Не указано'}</code>

{emoji['features']} <b>Признаки:</b>
{features_text}

{emoji['target']} <b>Целевая переменная:</b> <code>{model.target or 'Не указано'}</code>

{emoji['dates']} <b>Даты:</b>
├ Создана: <code>{created}</code>
└ Обновлена: <code>{updated}</code>

<b>🆔 ID модели:</b> <code>{model.id}</code>
"""
    
    return message.strip()


def format_features(features) -> str:
    """Форматирует список фич в красивый вид"""
    if not features:
        return "└ <i>Не указаны</i>"
    
    if isinstance(features, list):
        if len(features) == 1:
            return f"└ <code>{features[0]}</code>"
        else:
            features_lines = []
            for i, feature in enumerate(features[:10]):  # Ограничиваем показ
                prefix = "├" if i < len(features) - 1 else "└"
                features_lines.append(f"{prefix} <code>{feature}</code>")
            
            if len(features) > 10:
                features_lines.append(f"└ <i>... и еще {len(features) - 10} признаков</i>")
            
            return "\n".join(features_lines)
    else:
        return f"└ <code>{features}</code>"



@router.callback_query(F.data.startswith("create_ML_model"))
async def create_model_menu(callback: CallbackQuery, state: FSMContext):
    try:
        task_type = callback.data.split("_")[3].strip()
        await callback.message.answer(
            "Выберите существующую модель или создайте новую",
            reply_markup= inline_keyboards.list_ml_models(
                models,
                task = task_type
            )
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)
