from aiogram import Router
from aiogram.filters import Command
from .handler_app import any_input

def register_user_commands(router: Router):
    # router.message.register(start, Command(commands=['start']))
    router.message.register(any_input)