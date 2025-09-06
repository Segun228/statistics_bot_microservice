from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Iterable
from app.requests.get.get_sets import get_sets

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Каталог 📦", callback_data="catalogue")],
        [InlineKeyboardButton(text="Рассылка ✉️", callback_data="send_menu")],
        [InlineKeyboardButton(text="👤 Аккаунт", callback_data="account_menu")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")]
    ]
)

account_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Админ ⚙️", callback_data="admin_menu")],
        [InlineKeyboardButton(text="Запросить права администратора 👑", callback_data="request_admin")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)

delete_account_confirmation_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="delete_account")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="account_menu")],
    ]
)



home = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)

restart = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Главное меню", callback_data="restart")],
    ]
)


catalogue = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=" Каталог", callback_data="catalogue")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)

no_posts = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=" Создать пост ✍️", callback_data="catalogue")],
        [InlineKeyboardButton(text=" Каталог 📖", callback_data="catalogue")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)


async def get_catalogue(telegram_id, categories = None):
    if categories is None:
        categories = await get_sets(telegram_id=telegram_id)
    keyboard = InlineKeyboardBuilder()
    if categories and categories is not None:
        for category in categories:
            keyboard.add(InlineKeyboardButton(text=f"{category.get('name')}", callback_data=f"category_{category.get('id')}"))
    keyboard.add(InlineKeyboardButton(text="Создать категорию ✨", callback_data="create_category"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return keyboard.adjust(1).as_markup()


async def get_posts(posts, category):
    keyboard = InlineKeyboardBuilder()
    category_id = category.get("id", 0)
    if posts is None or posts == [] or posts == ():
        keyboard.add(InlineKeyboardButton(text="Каталог 📚", callback_data="catalogue"))
        keyboard.add(InlineKeyboardButton(text="Редактировать категорию ✏️", callback_data=f"edit_category_{category_id}"))
        keyboard.add(InlineKeyboardButton(text="Удалить категорию ❌", callback_data=f"delete_category_{category_id}"))
        keyboard.add(InlineKeyboardButton(text="Создать пост ➕", callback_data=f"create_post_{category_id}"))
        keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
        return keyboard.adjust(1).as_markup()
    for post in posts:
        keyboard.add(InlineKeyboardButton(text=f"{post.get('title', 'Прекрасное растение')}", callback_data=f"post_{category_id}_{post.get('id')}"))
    keyboard.add(InlineKeyboardButton(text="Редактировать категорию ✏️", callback_data=f"edit_category_{category_id}"))
    keyboard.add(InlineKeyboardButton(text="Удалить категорию ❌", callback_data=f"delete_category_{category_id}"))
    keyboard.add(InlineKeyboardButton(text="Создать пост ➕", callback_data=f"create_post_{category_id}"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return keyboard.adjust(1).as_markup()



async def get_post_menu(category_id, post_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Добавить фото 📸", callback_data=f"add_photo_{post_id}"))
    keyboard.add(InlineKeyboardButton(text="Редактировать пост 📝", callback_data=f"edit_post_{category_id}_{post_id}"))
    keyboard.add(InlineKeyboardButton(text="Удалить пост 🗑️", callback_data=f"delete_post_{category_id}_{post_id}"))
    keyboard.add(InlineKeyboardButton(text="Каталог 📦", callback_data="catalogue"))
    keyboard.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return keyboard.adjust(1).as_markup()


async def give_acess(user_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Разрешить ✅", callback_data=f"access_give_{user_id}"))
    keyboard.add(InlineKeyboardButton(text="Отклонить ❌", callback_data=f"access_reject_{user_id}"))
    return keyboard.adjust(1).as_markup()



file_panel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Получить отчет 📈", callback_data="get_report")],
        [InlineKeyboardButton(text="Дополнить ассортимент 📝", callback_data="add_posts")],
        [InlineKeyboardButton(text="Обновить ассортимент 🔄", callback_data="replace_posts")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ]
)