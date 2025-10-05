from aiogram import Router
from app.filters.IsAdmin import IsAdmin

admin_router = Router(name="admin")
user_router = Router(name="user")
distribution_router = Router(name="distribution")
dataset_router = Router(name="dataset")
catcher_router = Router(name="catcher")
