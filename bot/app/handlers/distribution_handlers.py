from app.handlers.router import distribution_router as router
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

from app.keyboards import inline_user as inline_keyboards

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

from app.requests.distribution.get_plot import get_plot

@router.callback_query(F.data.startswith("get_plot_"))
async def get_plot_start(callback: CallbackQuery, state: FSMContext, bot:Bot):
    try:
        id = int(callback.data.split("_")[2])
        await state.clear()
        zip_buf = await get_plot(
            telegram_id= callback.from_user.id,
            id = id,
        )
        if not zip_buf:
            raise Exception("Error while getting report from the server")
        zip_buf = io.BytesIO(zip_buf)
        with zipfile.ZipFile(zip_buf, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if filename.endswith(('.png', '.img', '.jpg', '.jpeg')): 
                    file_bytes = zip_ref.read(filename)
                    file_buf = io.BytesIO(file_bytes)
                    file_buf.seek(0)

                    document = BufferedInputFile(file_buf.read(), filename=filename)
                    await bot.send_document(chat_id=callback.from_user.id, document=document)
        await callback.message.answer("Ваше распределение готово!", reply_markup= inline_keyboards.main)

    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Возникла ошибка при анализе", reply_markup= inline_keyboards.main)
        raise
    finally:
        await state.clear()
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="visualize_set"
    )

@router.callback_query(F.data.startswith("get_probability_"))
async def get_probability_start(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(F.data.startswith("get_interval_"))
async def get_interval_start(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(F.data.startswith("get_quantile_"))
async def get_quantile_start(callback: CallbackQuery, state: FSMContext):
    pass

@router.callback_query(F.data.startswith("get_percentile_"))
async def get_percentile_start(callback: CallbackQuery, state: FSMContext):
    pass