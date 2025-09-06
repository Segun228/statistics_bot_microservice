from app.handlers.router import admin_router as router
import logging
import re
import zipfile
import io
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

from app.states.states import Send, File, Distribution, Dataset

from aiogram.types import BufferedInputFile


from app.keyboards.inline_user import get_catalogue, get_posts

from app.filters.IsAdmin import IsAdmin

from app.requests.user.login import login
from app.requests.helpers.get_cat_error import get_cat_error_async
from app.requests.get.get_sets import get_sets, retrieve_set
from app.requests.get.get_post import get_post

from app.requests.helpers.get_cat_error import get_cat_error_async

from bot.app.requests.post.post_dataset import post_set
from app.requests.post.postPost import post_post
from bot.app.requests.put.put_distribution import put_set
from app.requests.put.putPost import put_post
from bot.app.requests.delete.deleteDistribution import delete_category
from app.requests.delete.deletePost import delete_post
from app.requests.user.get_alive import get_alive
from app.requests.user.make_admin import make_admin

from app.requests.files.get_report import get_report
from app.requests.files.put_report import put_report

from app.requests.units import get_unit_report, get_unit_bep, get_unit_exel
from app.requests.put import update_model_cohort_data
from app.requests.units.get_unit_cohort import get_unit_cohort

from app.requests.sets.set_generate_report import set_generate_report
from app.requests.sets.set_visualize import set_visualize
from app.requests.sets.get_set_cohort import get_set_cohort


from app.kafka.utils import build_log_message

from app.requests.sets.set_text_report import set_text_report
#===========================================================================================================================
# Конфигурация основных маршрутов
#===========================================================================================================================


@router.message(CommandStart(), IsAdmin())
async def cmd_start_admin(message: Message, state: FSMContext):
    data = await login(telegram_id=message.from_user.id)
    if data is None:
        logging.error("Error while logging in")
        await message.answer("Бот еще не проснулся, попробуйте немного подождать 😔", reply_markup=inline_keyboards.restart)
        return
    await state.update_data(telegram_id = data.get("telegram_id"))
    await message.reply("Приветствую! 👋")
    await message.answer("Я предоставляю полный инструментарий для МатСтата и АБтестов")
    await message.answer("Сейчас ты можешь создавать, удалять и изменять распределения, а также добавлять свои датасеты в формате CSV")
    await message.answer("Я много что умею 👇", reply_markup=inline_keyboards.main)
    await state.clear()
    build_log_message(
        telegram_id=message.from_user.id,
        action="command",
        source="command",
        payload="start"
    )


@router.callback_query(F.data == "restart")
async def callback_start_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    data = await login(telegram_id=callback.from_user.id)
    if data is None:
        logging.error("Error while logging in")
        await callback.message.answer("Бот еще не проснулся, попробуйте немного подождать 😔", reply_markup=inline_keyboards.restart)
        return
    await state.update_data(telegram_id = data.get("telegram_id"))
    await callback.message.reply("Приветствую! 👋")
    await callback.message.answer("Я предоставляю полный инструментарий для МатСтата и АБтестов")
    await callback.message.answer("Сейчас ты можешь создавать, удалять и изменять распределения, а также добавлять свои датасеты в формате CSV")
    await callback.answer()
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="restart"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    build_log_message(
        telegram_id=message.from_user.id,
        action="command",
        source="command",
        payload="help"
    )
    await message.reply(text="Этот бот предоставляет доступ к инструментам статистического анализа, а также он специализирован для проведения АБ тестов\n\n Он может выполнять несколько интересных функций \n\nВы можете выбирать интересующие вас функции, в каждой из них вам будут предоставлены инструкции\n\nЕсли у вас остались вопросы, звоните нам или пишите в тех поддержку, мы всегда на связи:\n\n@dianabol_metandienon_enjoyer", reply_markup=inline_keyboards.home)

@router.message(Command("contacts"))
async def cmd_contacts(message: Message):
    build_log_message(
        telegram_id=message.from_user.id,
        action="command",
        source="command",
        payload="contacts"
    )
    text = "Связь с разрабом: 📞\n\n\\@dianabol\\_metandienon\\_енjoyer 🤝"
    await message.reply(text=text, reply_markup=inline_keyboards.home, parse_mode='MarkdownV2')

@router.callback_query(F.data == "contacts")
async def contacts_callback(callback: CallbackQuery):
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="menu",
        payload="contacts"
    )
    text = "Связь с разрабом: 📞\n\n\\@dianabol\\_metandienon\\_enjoyer 🤝"
    await callback.message.edit_text(text=text, reply_markup=inline_keyboards.home, parse_mode='MarkdownV2')
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="menu",
        payload="main_menu"
    )
    await callback.message.answer("Я много что умею 👇", reply_markup=inline_keyboards.main)
    await callback.answer()

#===========================================================================================================================
# Каталог
#===========================================================================================================================
@router.callback_query(F.data == "catalogue")
async def catalogue_callback_admin(callback: CallbackQuery):
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="menu",
        payload="catalogue"
    )
    categories = await get_sets(telegram_id=callback.from_user.id)
    await callback.message.answer("Что именно вас интересует?👇", reply_markup = inline_keyboards.catalogue_choice)
    await callback.answer()


@router.callback_query(F.data == "distributions")
async def get_distributions_catalogue(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Отлично, вот ваши распределения!", reply_markup = await inline_keyboards.get_distributions_catalogue(telegram_id=callback.from_user.id))



@router.callback_query(F.data == "datasets")
async def get_datasets_catalogue(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Отлично, вот ваши датасеты!", reply_markup = await inline_keyboards.get_datasets_catalogue(telegram_id=callback.from_user.id))


@router.callback_query(F.data.startswith("distribution_"))
async def category_catalogue_callback_admin(callback: CallbackQuery):
    await callback.answer()
    category_id = callback.data.split("_")[1]
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="menu",
        payload=f"category_{category_id}"
    )
    categories = await get_sets(telegram_id=callback.from_user.id)
    current_category = None
    if categories is not None:
        for category in categories:
            if str(category.get("id")) == str(category_id):
                current_category = category
                break
    
    if current_category is None or current_category.get("units") is None or current_category.get("units") == []:
        await callback.message.answer("Извините, тут пока пусто, возвращаейтесь позже!", reply_markup= await get_posts(posts=current_category.get("units"), category=current_category ))
        await callback.answer()
        return
    await callback.message.answer("Вот доступные модели юнит-экономики👇", reply_markup= await get_posts(category= current_category ,posts = current_category.get("units", [])))




#===========================================================================================================================
# Создание сета
#===========================================================================================================================
"""

@router.callback_query(F.data == "create_category")
async def category_create_callback_admin(callback: CallbackQuery, state: FSMContext):
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="create_category"
    )
    await state.clear()
    await callback.message.answer("Введите название набора моделей экономики")
    await state.set_state(Set.handle_set)
    await callback.answer()


@router.message(Set.handle_set)
async def category_create_callback_admin_description(message: Message, state: FSMContext):
    name = (message.text).strip()
    await state.update_data(name = name)
    await message.answer("Введите описание набора моделей экономики")
    await state.set_state(Set.description)


@router.message(Set.description)
async def category_enter_name_admin(message: Message, state: FSMContext):
    description = (message.text).strip()
    data = await state.get_data()
    name = data.get("name")
    response = await post_set(telegram_id=message.from_user.id, name=name, description= description)
    if not response:
        await message.answer("Извините, не удалось создать набор моделей", reply_markup=inline_keyboards.main)
        return
    await message.answer("Набор моделей создан!", reply_markup= await get_catalogue(telegram_id = message.from_user.id))
    await state.clear()


#===========================================================================================================================
# Редактирование сета
#===========================================================================================================================
@router.callback_query(F.data.startswith("edit_category_"))
async def category_edit_callback_admin(callback: CallbackQuery, state: FSMContext):
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="edit_set"
    )
    await callback.answer()
    await state.clear()
    category_id = callback.data.split("_")[2]
    await state.set_state(Set.handle_edit_set)
    await state.update_data(category_id = category_id)
    await callback.message.answer("Введите новое название сета")


@router.message(Set.handle_edit_set)
async def category_edit_callback_admin_description(message: Message, state: FSMContext):
    name = (message.text).strip()
    await state.update_data(name = name)
    await message.answer("Введите новое описание набора моделей экономики")
    await state.set_state(Set.edit_description)


@router.message(Set.edit_description)
async def category_edit_name_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data.get("category_id")
    name = data.get("name")
    description = (message.text).strip()
    response = await put_set(telegram_id=message.from_user.id, name=name, category_id=category_id, description=description)
    if not response:
        await message.answer("Извините, не удалось отредактировать сет", reply_markup=inline_keyboards.main)
        return
    await message.answer("Сет отредактирован!", reply_markup=await get_catalogue(telegram_id = message.from_user.id))
    await state.clear()

#===========================================================================================================================
# Удаление сета   
#===========================================================================================================================

@router.callback_query(F.data.startswith("delete_category_"))
async def category_delete_callback_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    category_id = callback.data.split("_")[2]
    response = await delete_category(telegram_id=callback.from_user.id, category_id=category_id)
    if not response:
        await callback.message.answer("Извините, не удалось удалить категорию", reply_markup=inline_keyboards.main)
        return
    await callback.message.answer("Категория удалена!", reply_markup=await get_catalogue(telegram_id = callback.from_user.id))
    await state.clear()
    build_log_message(
        telegram_id=callback.from_user.id,
        action="callback",
        source="inline",
        payload="delete_set"
    )



#===========================================================================================================================
# Разрешение доступа
#===========================================================================================================================


@router.callback_query(F.data.startswith("access_give"))
async def give_acess_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    request = str(callback.data)
    try:
        user_id = list(request.split("_"))[2]
        if not user_id:
            logging.error("Ошибка предоставления доступа")
            return
        response = await make_admin(
            telegram_id= callback.from_user.id,
            target_user_id= user_id
        )
        if not response:
            logging.error("Ошибка предоставления доступа")
            await bot.send_message(chat_id=int(user_id), text="К сожалению, вам было отказано в предоставлении прав администратора", reply_markup=inline_keyboards.home)
        else:
            logging.info(response)
            await callback.message.answer("Права администратора были успешно предоставлены", reply_markup=inline_keyboards.home)
            await bot.send_message(chat_id=user_id, text="Вам были предоставлены права администратора", reply_markup=inline_keyboards.home)
    except Exception as e:
        logging.error(e)


@router.callback_query(F.data.startswith("access_reject"))
async def reject_acess_admin(callback: CallbackQuery, state: FSMContext, bot:Bot):
    request = str(callback.data)
    try:
        user_id = list(request.split("_"))[2]
        await bot.send_message(chat_id=int(user_id), text="К сожалению, вам было отказано в предоставлении прав администратора", reply_markup=inline_keyboards.home)
    except Exception as e:
        logging.error(e)
    finally:
        await state.clear()
"""
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