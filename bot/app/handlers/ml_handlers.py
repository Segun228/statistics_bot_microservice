from app.handlers.router import ml_router as router
import logging
import re
import zipfile
import io
import json
import re
from aiogram.types import BufferedInputFile
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

from app.states.states import CreateModel

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
from app.states.states import FitModel, RefitModel, PredictModel, DeleteModel, GenerateSample


from app.requests.dataset import stats_handlers
from app.requests.ml_models.get_all_models import get_all_models, retrieve_model, post_model, delete_model
from app.requests.ml_models.mlflow import fit_model, refit_model, predict_model
from math import floor, ceil

from app.requests.ml_models.mlflow import get_sample

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

def check_none(val, name="given value"):
    if val is None:
        raise ValueError("The invalid value in {name}")

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


def format_model_info(model_dict) -> str:
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
    
    # Получаем значения из словаря
    name = model_dict.get('name') or 'Не указано'
    description = model_dict.get('description') or 'Не указано'
    task = model_dict.get('task_display') or model_dict.get('task') or 'Не указано'
    model_type = model_dict.get('type_display') or model_dict.get('type') or 'Не указано'
    features = model_dict.get('features')
    target = model_dict.get('target') or 'Не указано'
    model_id = model_dict.get('id', 'Не указано')
    
    # Форматируем даты
    created_at = model_dict.get('created_at')
    updated_at = model_dict.get('updated_at')
    
    created = created_at.strftime("%d.%m.%Y %H:%M") if hasattr(created_at, 'strftime') else "Не указано"
    updated = updated_at.strftime("%d.%m.%Y %H:%M") if hasattr(updated_at, 'strftime') else "Не указано"

    features_text = format_features(features)
    
    message = f"""
<b>🤖 МАШИННОЕ ОБУЧЕНИЕ | МОДЕЛЬ</b>

{emoji['name']} <b>Название:</b> <code>{name}</code>

{emoji['description']} <b>Описание:</b>
{description}

{emoji['task']} <b>Задача:</b> <code>{task}</code>

{emoji['type']} <b>Тип модели:</b> <code>{model_type}</code>

{emoji['features']} <b>Признаки:</b>
{features_text}

{emoji['target']} <b>Целевая переменная:</b> <code>{target}</code>

{emoji['dates']} <b>Даты:</b>
├ Создана: <code>{created}</code>
└ Обновлена: <code>{updated}</code>

<b>🆔 ID модели:</b> <code>{model_id}</code>
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

#==============================================================================================================
# Создание модели
#==============================================================================================================


@router.callback_query(F.data.startswith("create_ML_model"))
async def create_model_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(CreateModel.start_create)
        task_type = callback.data.split("_")[3].strip()
        await state.update_data(task = task_type)
        await callback.message.answer(
            "Какой тип модели вы хотите выбрать?",
            reply_markup= inline_keyboards.list_ml_algorithms(
                task = task_type
            )
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)




@router.callback_query(CreateModel.start_create)
async def select_model_name(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(CreateModel.name)
        model_type = callback.data.replace("create_model_", "").strip()
        await state.update_data(type=model_type)
        await callback.message.answer(
            "Введите имя вашей модели"
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)




@router.message(CreateModel.name)
async def select_model_description(message:Message, state: FSMContext):
    try:
        await state.set_state(CreateModel.description)
        name = message.text.strip()
        await state.update_data(name = name)
        await message.answer(
            "Введите описание вашей модели"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.message(CreateModel.description)
async def load_model_file(message:Message, state: FSMContext):
    try:
        await state.set_state(CreateModel.file)
        description = message.text.strip()
        await state.update_data(description = description)
        await message.answer(
            "Загрузите CSV файл с вашим датасетом"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.message(F.document, CreateModel.file)
async def get_model_dataset_file_message(message: Message, state: FSMContext, bot:Bot):
    try:
        await state.set_state(CreateModel.target)
        file_id = message.document.file_id
        file_name = message.document.file_name
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_bytes = await bot.download_file(file_path)
        buffer = io.BytesIO()
        buffer.write(file_bytes.read())
        buffer.seek(0)  
        await state.update_data(dataset = buffer)
        df = pd.read_csv(
            buffer
        )
        buffer.seek(0)
        cols = df.columns
        await state.update_data(columns = cols)
        await message.answer("Выберите колоку с таргетом", reply_markup=inline_keyboards.select_target_column(columns = cols))
    except Exception as e:
        logging.exception(e)
        logging.error("Error while loading the dataset")


@router.callback_query(CreateModel.target)
async def finish_creation(callback: CallbackQuery, state: FSMContext):
    from pprint import pprint
    try:
        data = await state.get_data()
        columns = data.get("columns", [])
        target = callback.data.split("_")[2].strip()
        name = data.get("name")
        description = data.get("description")
        type = data.get("type")
        task = data.get("task")
        dataset = data.get("dataset")
        features = [el for el in columns if el != target]
        response = await post_model(
            telegram_id = callback.from_user.id,
            csv_buffer = dataset,
            name = name,
            description = description,
            target = target,
            features = list(features),
            task = task,
            type = type
        )
        await callback.message.answer("Модель создана! Теперь вы можете делать предсказания, дообучать или обучать модель заново")
        await callback.message.answer("Обратите внимание, что часть признаков могла быть убрана как неэффективные или деструктивные",
            reply_markup=inline_user_keyboards.catalogue
        )
        await state.clear()

    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка при обработке результатов, попробуйте позже.", 
                                        reply_markup=inline_user_keyboards.home)
        await state.clear()


#==============================================================================================================
# Предсказание модели
#==============================================================================================================


@router.callback_query(F.data.startswith("model_predict_"))
async def model_make_prediction(callback: CallbackQuery, state: FSMContext):
    try:
        model_id = int(callback.data.strip().split("_")[2])
        await callback.message.answer("Вам будет необходимо сбросить файл с значениями признаков. Внимание, все строки с пустыми значениями будут удалены")
        await state.set_state(PredictModel.start_predict)
        await state.update_data(id = model_id)
        mod = await retrieve_model(
            telegram_id=callback.from_user.id,
            model_id=model_id
        )
        if not mod or mod is None:
            raise ValueError("Error while getting the single model")
        await callback.message.answer(
            "Ваши фичи:\n"+
            ("\n\n".join(mod.get("features"))),
        )
        await state.update_data(columns = mod.get("features"))
        await state.update_data(target = mod.get("target"))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.message(F.document, PredictModel.start_predict)
async def finish_prediction(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.set_state(PredictModel.finish_predict)

        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        if not file_path:
            await message.answer("❌ Ошибка при получении файла")
            return

        file_bytes = await bot.download_file(file_path)
        buffer = BytesIO()
        buffer.write(file_bytes.read())
        buffer.seek(0)

        try:
            df = pd.read_csv(buffer)
        except Exception as e:
            await message.answer("❌ Ошибка чтения CSV файла")
            return

        data = await state.get_data()
        state_cols = data.get("columns", [])
        model_id = data.get("id")

        if not state_cols:
            await message.answer("❌ Не найдены ожидаемые колонки")
            return

        if not model_id:
            await message.answer("❌ Не найден ID модели")
            return

        missing_cols = [col for col in state_cols if col not in df.columns]
        if missing_cols:
            await message.answer(f"❌ В файле отсутствуют колонки: {', '.join(missing_cols)}")
            return

        try:
            df_selected = df[state_cols].copy()
        except Exception as e:
            await message.answer("❌ Ошибка при выборе колонок")
            return

        df_clean = df_selected.dropna()
        if len(df_clean) == 0:
            await message.answer("❌ После очистки данных не осталось строк")
            return

        await message.answer("📊 Обрабатываю данные...")

        response = await predict_model(
            telegram_id=message.from_user.id,
            model_id=model_id,
            df=df_clean
        )

        await state.clear()

        if response and len(response) > 0:
            try:

                zip_buffer = BytesIO(response)

                with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                    if 'predictions.csv' in zip_file.namelist():
                        with zip_file.open('predictions.csv') as csv_file:
                            csv_data = csv_file.read()
                        csv_buffer = BufferedInputFile(
                            csv_data,
                            filename="predictions.csv"
                        )
                        await message.answer_document(
                            csv_buffer,
                            caption="📊 Результаты предсказания"
                        )
                        if 'images.zip' in zip_file.namelist():
                            await message.answer("📈 Генерирую графики...")
                            with zip_file.open('images.zip') as images_zip:
                                images_data = images_zip.read()
                                images_buffer = BytesIO(images_data)
                            with zipfile.ZipFile(images_buffer, 'r') as images_archive:
                                for image_name in images_archive.namelist():
                                    if image_name.endswith('.png'):
                                        with images_archive.open(image_name) as img_file:
                                            img_data = img_file.read()
                                            await message.answer_photo(
                                                photo=BufferedInputFile(img_data, filename=image_name),
                                                caption=f"📈 {image_name.replace('.png', '')}"
                                            )
                    else:
                        await message.answer("❌ В архиве не найден файл с предсказаниями")
                        
            except zipfile.BadZipFile:
                try:
                    error_text = response.decode('utf-8')
                    if error_text.startswith('{'):
                        error_data = json.loads(error_text)
                        await message.answer(f"❌ Ошибка: {error_data.get('error', 'Unknown error')}")
                    else:
                        await message.answer(f"❌ Ошибка сервера: {error_text[:500]}")
                except:
                    await message.answer("❌ Неизвестный формат ответа от сервера")
            except Exception as e:
                await message.answer(f"❌ Ошибка при обработке архива: {str(e)}")
        else:
            await message.answer("❌ Сервер не вернул данные")
            
    except Exception as e:
        logging.exception(f"Error in finish_prediction: {e}")
        await message.answer("❌ Произошла ошибка при обработке файла")


#==============================================================================================================
# Генерация выборки
#==============================================================================================================

@router.callback_query(F.data.startswith("geterate_sample_"))
async def model_start_generating_sample(callback: CallbackQuery, state: FSMContext):
    try:
        model_task = callback.data.split("_")[2]
        await state.set_state(GenerateSample.start)
        await state.update_data(
            task = model_task
        )
        await callback.message.answer(
            "Введите общее количество признаков (с учетом бесполезных)"
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Ошибка во время генерации выборки")


@router.message(GenerateSample.start)
async def model_enter_features(message: Message, state: FSMContext):
    try:
        if not message.text:
            raise Exception("Error messafe format")
        total_features = int(message.text)
        await state.set_state(GenerateSample.features)
        await state.update_data(
            total_features = total_features
        )
        await message.answer(
            "Введите количество значимых признаков"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Ошибка во время генерации выборки")


@router.message(GenerateSample.features)
async def model_enter_meaning_features(message: Message, state: FSMContext):
    try:
        if not message.text:
            raise Exception("Error messafe format")
        meaning_features = int(message.text)
        await state.set_state(GenerateSample.meaning)
        await state.update_data(
            meaning_features = meaning_features
        )
        await message.answer(
            "Введите количество элементов выборки"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Ошибка во время генерации выборки")


@router.message(GenerateSample.meaning)
async def model_enter_number_samples(message: Message, state: FSMContext):
    try:
        if not message.text:
            raise Exception("Error messafe format")
        numbers = int(message.text)
        await state.set_state(GenerateSample.noise)
        await state.update_data(
            n = numbers
        )
        await message.answer(
            "Введите шум выборки (дробь от 0 до 1 формата 0.233)"
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Ошибка во время генерации выборки")


@router.message(GenerateSample.noise)
async def model_enter_noise(message: Message, state: FSMContext, bot:Bot):
    try:
        if not message.text:
            raise Exception("Error messafe format")
        noise = float(message.text)
        await state.set_state(GenerateSample.noise)
        data = await state.get_data()
        n = data.get("n", 1000)
        meaning_features = data.get("meaning_features", 1000)
        total_features = data.get("total_features", 1000)
        task = data.get("task", 1000)
        await message.answer(
            "Собираю вам выборку..."
        )
        sample = get_sample(
            task = task,
            n = n,
            noise = noise,
            meaning_features = meaning_features,
            total_features = total_features,
            random_state = np.random.randint(
                low=0,
                high=1000
            )
        )
        document = BufferedInputFile(sample, filename="sample.csv")
        await bot.send_document(
            chat_id=message.from_user.id,
            document=document
        )
    except Exception as e:
        logging.exception(e)
        await message.answer("Ошибка во время генерации выборки")

#==============================================================================================================
# Дообучение модели
#==============================================================================================================

@router.callback_query(F.data.startswith("model_fit_"))
async def model_make_fit(callback: CallbackQuery, state: FSMContext):
    try:
        model_id = int(callback.data.strip().split("_")[2])
        await callback.message.answer("Вам будет необходимо сбросить файл с значениями признаков и таргета. Внимание, все строки с пустыми значениями будут удалены")
        await state.set_state(FitModel.start_fit)
        await state.update_data(id = model_id)
        mod = await retrieve_model(
            telegram_id=callback.from_user.id,
            model_id=model_id
        )
        if not mod or mod is None:
            raise ValueError("Error while getting single model")
        await callback.message.answer(
            "\n\n".join(mod.get("features")),
        )
        await state.update_data(features = mod.get("features"))
        await state.update_data(target = mod.get("target"))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.message(F.document, FitModel.start_fit)
async def finish_fit(message: Message, state: FSMContext, bot:Bot):
    try:
        await state.set_state(PredictModel.finish_predict)
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_bytes = await bot.download_file(file_path)
        buffer = io.BytesIO()
        buffer.write(file_bytes.read())
        buffer.seek(0)  
        await state.update_data(dataset = buffer)
        df = pd.read_csv(
            buffer
        )
        cols = df.columns
        data = await state.get_data()
        state_cols = data.get("features")
        target = data.get("target")
        if not state_cols or not target:
            raise Exception("Error while comparing given columns")
        if target not in cols:
            raise Exception(f"The column {target} was not found")
        for col in state_cols:
            if col not in cols:
                raise Exception(f"The column {col} was not found")
        response = await fit_model(
            telegram_id = message.from_user.id,
            model_id = data.get("id"),
            df = df
        )
        await state.clear()
        if response and len(response) > 0:
            try:
                zip_buffer = BytesIO(response)
                with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                    if 'predictions.json' in zip_file.namelist():
                        with zip_file.open('predictions.json') as json_file:
                            json_data = json_file.read()
                        js = json.loads(json_data)
                        result_str = ""
                        for key, value in js.items():
                            result_str += f"{key}: {value}\n\n"
                        await message.answer(
                            result_str,
                        )
                        if 'images.zip' in zip_file.namelist():
                            await message.answer("📈 Генерирую графики...")
                            with zip_file.open('images.zip') as images_zip:
                                images_data = images_zip.read()
                                images_buffer = BytesIO(images_data)
                            with zipfile.ZipFile(images_buffer, 'r') as images_archive:
                                for image_name in images_archive.namelist():
                                    if image_name.endswith('.png'):
                                        with images_archive.open(image_name) as img_file:
                                            img_data = img_file.read()
                                            await message.answer_photo(
                                                photo=BufferedInputFile(img_data, filename=image_name),
                                                caption=f"📈 {image_name.replace('.png', '')}"
                                            )
                    else:
                        await message.answer("❌ В архиве не найден файл с предсказаниями")
                        
            except zipfile.BadZipFile:
                try:
                    error_text = response.decode('utf-8')
                    if error_text.startswith('{'):
                        error_data = json.loads(error_text)
                        await message.answer(f"❌ Ошибка: {error_data.get('error', 'Unknown error')}")
                    else:
                        await message.answer(f"❌ Ошибка сервера: {error_text[:500]}")
                except Exception as e:
                    logging.exception(e)
                    await message.answer("❌ Неизвестный формат ответа от сервера")
            except Exception as e:
                logging.exception(e)
                await message.answer(f"❌ Ошибка при обработке архива: {str(e)}")
        else:
            await message.answer("❌ Сервер не вернул данные")
            
        await state.clear()
    except Exception as e:
        logging.exception(e)
        logging.error("Error while fitting the model")


#==============================================================================================================
# Обучение модели с нуля
#==============================================================================================================


@router.callback_query(F.data.startswith("model_refit_"))
async def model_start_make_refit(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(RefitModel.confirm)
        model_id = callback.data.strip().split("_")[2]
        check_none(model_id)
        model_id = int(model_id)
        await callback.message.answer("Внимание!\n\nВы собираетесь полностью снести обученную модель, и обучить ее заново, вы уверены?", reply_markup=inline_keyboards.confirm(model_id))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("decline_"), RefitModel.confirm)
async def model_decline_refit(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.answer("Обучение с нуля отменено", reply_markup=inline_user_keyboards.catalogue)
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("confirm_"), RefitModel.confirm)
async def model_confirm_refit(callback: CallbackQuery, state: FSMContext):
    try:
        model_id = int(callback.data.strip().split("_")[1])
        await callback.message.answer("Вам будет необходимо сбросить файл с значениями признаков. Внимание, все строки с пустыми значениями будут удалены")
        await state.set_state(RefitModel.start_refit)
        await state.update_data(id = model_id)
        mod = await retrieve_model(
            telegram_id=callback.from_user.id,
            model_id=model_id
        )
        if not mod or mod is None:
            raise ValueError("Error while getting single model")
        await callback.message.answer(
            "\n\n".join(mod.get("columns")),
        )
        await state.update_data(columns = mod.get("columns"))
        await state.update_data(target = mod.get("target"))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.message(F.document, RefitModel.start_refit)
async def finish_refit(message: Message, state: FSMContext, bot:Bot):
    try:
        await state.set_state(RefitModel.finish_refit)
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_bytes = await bot.download_file(file_path)
        buffer = io.BytesIO()
        buffer.write(file_bytes.read())
        buffer.seek(0)  
        await state.update_data(dataset = buffer)
        df = pd.read_csv(
            buffer
        )
        cols = df.columns
        data = await state.get_data()
        state_cols = data.get("features")
        target = data.get("target")
        if not state_cols or not target:
            raise Exception("Error while comparing given columns")
        if target not in cols:
            raise Exception(f"The column {target} was not found")
        for col in state_cols:
            if col not in cols:
                raise Exception(f"The column {col} was not found")
        response = await refit_model(
            telegram_id = message.from_user.id,
            model_id = data,
            df = df
        )
        await message.answer(f"{response if response else "Модель успешно доучена!"}")
        await state.clear()
    except Exception as e:
        logging.exception(e)
        logging.error("Error while fitting the model")


#==============================================================================================================
# Удаление модели
#==============================================================================================================


@router.callback_query(F.data.startswith("model_delete_"))
async def model_start_delete(callback: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(DeleteModel.confirm)
        model_id = callback.data.strip().split("_")[2]
        check_none(model_id)
        model_id = int(model_id)
        await callback.message.answer("Внимание!\n\nВы собираетесь полностью удалить модель, вы уверены?", reply_markup=inline_keyboards.confirm(model_id))
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("decline_"), DeleteModel.confirm)
async def model_decline_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.answer("Удаление модели отменено", reply_markup=inline_user_keyboards.catalogue)
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


@router.callback_query(F.data.startswith("confirm_"), DeleteModel.confirm)
async def model_confirm_delete(callback: CallbackQuery, state: FSMContext):
    try:
        model_id = int(callback.data.strip().split("_")[1])
        response = await delete_model(
            model_id=model_id,
            telegram_id=callback.from_user.id
        )
        logging.info(response)
        await state.clear()
        await callback.message.answer(
            "Модель успешно удалена!",
            reply_markup=inline_user_keyboards.catalogue
        )
    except Exception as e:
        logging.exception(e)
        await callback.message.answer("Произошла ошибка, попробуйте позже.", reply_markup=inline_user_keyboards.home)


#==============================================================================================================
# Полное реобучение модели
#==============================================================================================================


@router.callback_query(F.data.startswith("model_refit_"))
async def model_start_delete(callback: CallbackQuery, state: FSMContext):

