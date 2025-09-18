from app.handlers.router import dataset_router as router
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

from app.keyboards import inline_dataset as inline_keyboards

from app.states.states import Send, File, Distribution, Dataset, DistributionEdit, DatasetEdit, Errors, Groups, Confirm

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

from app.requests.dataset.patch_errors.patch_errors import patch_errors
from app.requests.dataset.patch_categories.patch_groups import set_groups

from app.keyboards.reply_dataset import create_reply_column_keyboard_group
from app.states.states import SampleSize


from app.requests.dataset import stats_handlers
from math import floor, ceil
#===========================================================================================================================
# Меню
#===========================================================================================================================

def escape_md_v2(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

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
# Установка альфа и бета
#===========================================================================================================================

@router.callback_query(F.data.startswith("set_errors_"))
async def set_errors(callback: CallbackQuery, state:FSMContext):
    try:
        dataset_id = int(callback.data.split("_")[2])
        await callback.message.answer("Выберите ошибку первого рода")
        await state.set_state(Errors.handle_errors)
        await state.update_data(id = dataset_id)
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await callback.message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)


@router.message(Errors.handle_errors)
async def alpha_errors(message:Message, state:FSMContext):
    try:
        alpha = float(message.text.strip())
        await state.update_data(alpha = alpha)
        await message.answer("Выберите ошибку второго рода")
        await state.set_state(Errors.alpha)
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)


@router.message(Errors.alpha)
async def beta_errors(message:Message, state:FSMContext):
    try:
        beta = float(message.text.strip())
        data = await state.get_data()
        dataset_id = data.get("id")
        alpha = data.get("alpha")
        response = await patch_errors(dataset_id = dataset_id, alpha = alpha, beta = beta, telegram_id=message.from_user.id)
        if response:
            await message.answer("Данные успешно обновлены!",reply_markup=await inline_keyboards.get_dataset_ab_menu(dataset_id=dataset_id))
        await state.set_state(Errors.alpha)
        await state.clear()
    except Exception as e:
        logging.error("An error occured")
        logging.exception(e)
        await message.answer("Извините, возникла ошибка. Попробуйте позже(", reply_markup=inline_user_keyboards.catalogue)


#===========================================================================================================================
# Установка теста и контроля
#===========================================================================================================================

@router.callback_query(F.data.startswith("set_groups"))
async def set_groups_start(callback: CallbackQuery, state:FSMContext):
    try:
        dataset_id = callback.data.split("_")[2]
        await state.set_state(Groups.handle)
        await state.update_data(id = dataset_id)
        dataset = await retrieve_dataset(
            telegram_id=callback.from_user.id,
            dataset_id=int(dataset_id)
        )
        if dataset is None:
            raise ValueError("Error while getting dataset info from the server")
        await state.update_data(
            columns = dataset.get("columns")
        )
        await callback.message.answer("Выберите тестовую группу", reply_markup=create_reply_column_keyboard_group(columns=dataset.get("columns")))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Извините, не удалось установить группы, попробуйте позже")


@router.message(Groups.handle)
async def set_control_group(message:Message, state:FSMContext):
    try:
        test_group = message.text.strip()
        await state.set_state(Groups.controle)
        await state.update_data(test = test_group)
        data = await state.get_data()
        columns = data.get("columns")
        await message.answer("Выберите контрольную группу", reply_markup=create_reply_column_keyboard_group(columns=columns))
    except Exception as e:
        logging.exception(e)
        await message.answer("Извините, не удалось установить группы, попробуйте позже")


@router.message(Groups.controle)
async def set_end_group(message:Message, state:FSMContext):
    try:
        controle_group = message.text.strip()
        data = await state.get_data()
        test = data.get("test")
        dataset_id = data.get("id")
        answer = await set_groups(
            telegram_id = message.from_user.id,
            dataset_id = dataset_id,
            test = test,
            control = controle_group
        )
        if answer:
            await message.answer("Группы успешно выбраны!", reply_markup=await inline_keyboards.get_dataset_ab_menu(dataset_id=dataset_id))
            current_dataset = await retrieve_dataset(telegram_id=message.from_user.id, dataset_id=dataset_id)
            if current_dataset is None:
                await message.answer("Извините, тут пока пусто, возвращаейтесь позже!", reply_markup= await get_distributions_catalogue(telegram_id=message.from_user.id))
                return
            data = current_dataset
            params = data['columns']
            param_string = "\n"
            for nam in params:
                param_string += f"*{nam}*\n"
            param_string += "\n"
            msg = (
                f"*Name:* {data['name']}\n\n"
                f"*Columns:* {param_string}"
                f"*Alpha:* {str(data['alpha']).replace(".", "\.")}\n"
                f"*Beta:* {str(data['beta']).replace(".", "\.")}\n\n"
                f"*Test group:* {str(data['test']).replace(".", "\.") or "Not set yet"}\n"
                f"*Controle group:* {str(data['control']).replace(".", "\.") or "Not set yet"}\n\n"
                f"*Final length:* {str(data['length']).replace(".", "\.") or "Not set yet"}\n"
            )
            await message.answer(msg, parse_mode="MarkdownV2", reply_markup=await inline_keyboards.get_dataset_single_menu(dataset_id = dataset_id))
        
    except Exception as e:
        logging.exception(e)
        await message.answer("Извините, не удалось установить группы, попробуйте позже")

#===========================================================================================================================
# рассчет N
#===========================================================================================================================

@router.callback_query(F.data.startswith("count_n"))
async def count_n_start(callback: CallbackQuery, state:FSMContext):
    try:
        await state.clear()
        dataset_id = callback.data.split("_")[2]
        await state.update_data(id = dataset_id)
        await callback.message.answer("Введите, какой минимальный эффект вы хотите обнаружить (в единицах измерения целевой метрики)")
        await state.set_state(SampleSize.mde)
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Извините, произошла ошибка, попробуйте позже")

def format_mde_message(result):
    from math import ceil

    MDE = escape_md_v2(str(result['MDE']))
    MDE_pct = escape_md_v2(f"{result['MDE_%']:.2f}")
    test_size = escape_md_v2(str(ceil(result['test_size'])))
    control_size = escape_md_v2(str(ceil(result['control_size'])))
    n_total = escape_md_v2(str(ceil(result['n_total'])))
    text = (
        f"*Расчёт MDE и размеров выборки*\n\n"
        f"📊 *Минимальная детектируемая разница \(MDE\)*:\n"
        f"`{MDE}` \({MDE_pct}%\)\n\n"
        f"👥 *Размеры выборок*\n"
        f"Тестовая группа: `{test_size}`\n"
        f"Контрольная группа: `{control_size}`\n"
        f"Общее количество: `{round(float(control_size))+round(float(test_size))}`"
    )
    return text

@router.message(SampleSize.mde)
async def count_n_end(message: Message, state: FSMContext):
    try:
        mde = float(message.text)
        if not mde:
            raise ValueError("Invalid MDE given")
        data = await state.get_data()
        dataset_id = data.get("id")
        await message.answer("Запускаю рассчеты...")

        response = await stats_handlers.count_n(
            telegram_id=message.from_user.id,
            id=dataset_id,
            mde=mde
        )
        if not response:
            raise ValueError("An error occurred during calculation")

        result = response if isinstance(response, dict) else json.loads(response.data)


        await message.answer(
            format_mde_message(result),
            parse_mode="MarkdownV2",
            reply_markup=await inline_keyboards.get_dataset_single_menu(dataset_id=dataset_id)
        )
        await state.clear()

    except Exception as e:
        logging.exception(e)
        await message.answer("Извините, произошла ошибка, попробуйте позже")


#===========================================================================================================================
# рассчет MDE
#===========================================================================================================================

@router.callback_query(F.data.startswith("count_mde"))
async def count_mde_start(callback: CallbackQuery, state:FSMContext):
    try:
        await state.clear()
        dataset_id = callback.data.split("_")[2]
        await callback.message.answer("Уже считаю, подождите немного...")
        response = await stats_handlers.count_n(
            telegram_id=callback.from_user.id,
            id=dataset_id,
        )
        if not response:
            raise ValueError("An error occurred during calculation")

        result = response if isinstance(response, dict) else json.loads(response.data)

        await callback.message.answer(
            format_mde_message(result),
            parse_mode="MarkdownV2",
            reply_markup=await inline_keyboards.get_dataset_single_menu(dataset_id=dataset_id)
        )
        await state.clear()
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Извините, произошла ошибка, попробуйте позже")

#===========================================================================================================================
# Z-test
#===========================================================================================================================

def format_test_message(response):
    try:
        result = response
        if type(result) is json or type(result) is str:
            result = json.loads(result)
        n1 = result.get('n1', '?')
        n2 = result.get('n2', '?')

        mean_control = result.get('mean_control', 0.0)
        mean_test = result.get('mean_test', 0.0)

        var_control = result.get('var_control', 0.0)
        var_test = result.get('var_test', 0.0)

        z = result.get('z', 0.0)
        p = result.get('p', 1.0)
        effect = result.get('effect', 0.0)

        pearson = result.get('pearson', 0.0)
        pearson_p = result.get('pearson_p', 1.0)

        spearman = result.get('spearman', 0.0)
        spearman_p = result.get('spearman_p', 1.0)

        warning = result.get('warning', '—')

        text = (
            f"*📊 Результаты Z\-теста*\n\n"
            f"*👥 Размеры групп:*\n"
            f"Контроль: `{escape_md_v2(n1)}`\n"
            f"Тест: `{escape_md_v2(n2)}`\n\n"

            f"*📈 Средние значения:*\n"
            f"Контроль: `{mean_control:.2f}`\n"
            f"Тест: `{mean_test:.2f}`\n\n"

            f"*📊 Дисперсии:*\n"
            f"Контроль: `{var_control:.2f}`\n"
            f"Тест: `{var_test:.2f}`\n\n"

            f"*🧪 Z\-статистика:* `{z:.3f}`\n"
            f"*📉 P\-значение:* `{p:.3f}`\n"
            f"*📐 Эффект:* `{"Найдено статистически значимое различие. Нулевая гипотеза отвергается" if int(effect)==1 else "Статистически значимого различия не найдено. Нулевая гипотеза не отвергается"}`\n\n"

            f"*📉 Корреляции:*\n"
            f"Пирсон: `{pearson:.3f}` \(p\-value \= `{pearson_p:.3f}`\)\n"
            f"Спирмен: `{spearman:.3f}` \(p\-value \= `{spearman_p:.3f}`\)\n\n"

            f"*⚠️ Предупреждение:*\n"
            f"{escape_md_v2(warning)}"
        )
        return text
    except Exception as e:
        logging.error(e)
        raise


@router.callback_query(F.data.startswith("ztest_"))
async def ztest_start(callback: CallbackQuery, state:FSMContext):
    try:
        await state.clear()
        dataset_id = callback.data.split("_")[1]
        await state.update_data(id = dataset_id)
        await state.set_state(Confirm.bundle)
        await callback.message.answer("Z-тест накладывает на данные ограничения")
        await callback.message.answer("Для корректности теста необходимо, чтобы при рассчете выборка была репрезентативна, а также дисперсия ген. совокупности совпадала с выборочной (особенности программного рассчета)")
        await callback.message.answer("При N<30 данные должны быть нормальными")
        await callback.message.answer("Вы уверены, что хотите продолжить?", reply_markup= await inline_keyboards.get_confirm_menu(
            true_callback = "confirm_ztest",
            false_callback = f"dataset_{dataset_id}"
        ))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Извините, произошла ошибка, попробуйте позже")


@router.callback_query(F.data.startswith("confirm_ztest"))
async def ztest_end(callback: CallbackQuery, state:FSMContext):
    try:
        data = await state.get_data()
        dataset_id = data.get("id")
        response = await stats_handlers.z_test(
            telegram_id=callback.from_user.id,
            id=dataset_id,
        )
        if not response:
            raise ValueError("An error occurred during calculation")

        result = response if isinstance(response, dict) else json.loads(response.data)

        await callback.message.answer(
            format_test_message(response = result),
            parse_mode="MarkdownV2",
            reply_markup=await inline_keyboards.get_dataset_single_menu(dataset_id=dataset_id)
        )
        await state.clear()
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Извините, произошла ошибка, попробуйте позже")

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