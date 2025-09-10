from app.handlers.router import dataset_router as router
import logging
import re
import zipfile
import io
import json
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

from app.keyboards import inline_dataset as inline_keyboards

from app.states.states import Send, File, Distribution, Dataset, DistributionEdit, DatasetEdit

from aiogram.types import BufferedInputFile


from app.keyboards.inline_user import get_datasets_catalogue, get_distributions_catalogue

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


#===========================================================================================================================
# Меню
#===========================================================================================================================

@router.callback_query(F.data.startswith("ab_tests"))
async def get_datasets_ab_test_menu(callback: CallbackQuery):
    try:
        dataset_id = int(callback.data.split("_")[2])
        await callback.message.answer("Выберите необходимый инструмент", reply_markup=await inline_keyboards.get_dataset_ab_menu(dataset_id=dataset_id))
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await callback.message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)


@router.callback_query(F.data.startswith("ml_algorithms"))
async def get_datasets_ml_algo_menu(callback: CallbackQuery):
    try:
        dataset_id = int(callback.data.split("_")[2])
        await callback.message.answer("Выберите необходимый алгоритм", reply_markup=await inline_keyboards.get_dataset_ml_menu(dataset_id=dataset_id))
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await callback.message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)


@router.callback_query(F.data.startswith("get_criteria_"))
async def get_datasets_ab_criteria_menu(callback: CallbackQuery):
    try:
        dataset_id = int(callback.data.split("_")[2])
        await callback.message.answer("Выберите необходимый алгоритм", reply_markup=await inline_keyboards.get_dataset_criteria_menu(dataset_id=dataset_id))
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await callback.message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)



#===========================================================================================================================
# Заглушка
#===========================================================================================================================

@router.message()
async def all_other_messages(message: Message):
    await message.answer("Неизвестная команда 🧐")
    photo_data = await get_cat_error_async()
    if photo_data:
        photo_to_send = BufferedInputFile(photo_data, filename="cat_error.jpg")
        await message.bot.send_photo(chat_id=message.chat.id, photo=photo_to_send)


async def send_post_photos(callback: CallbackQuery, post: Dict[str, Any]):
    photo_ids = post.get('photos', [])

    if not photo_ids:
        await callback.message.answer("К сожалению, у этой позиции нет фотографий. 🖼️")
        return

    first_photo_id = photo_ids[0]
    caption_text = f"**{post.get('title', 'Без названия')}**"
    
    await callback.message.answer_photo(
        photo=first_photo_id,
        caption=caption_text,
        parse_mode="MarkdownV2"
    )

    for photo_id in photo_ids[1:]:
        await callback.message.answer_photo(photo=photo_id)
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="undefined"
    )

#===========================================================================================================================
# Отлов неизвестных обработчиков
#===========================================================================================================================

@router.callback_query()
async def unknown_callback(callback: CallbackQuery):
    logging.info(f"UNHANDLED CALLBACK: {callback.data}")
    await callback.answer(f"⚠️ Это действие не распознано. Получено: {callback.data}", show_alert=True)
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="undefined"
    )