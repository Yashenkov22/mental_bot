from aiogram import types
from config import ADMIN_ID

def admin_only(func):
    async def wrapped(*args, **kwargs):
        message = None
        for arg in args:
            if isinstance(arg, types.Message):
                message = arg
                break
        if message.from_user.id == int(ADMIN_ID):
            return await func(*args, **kwargs)
        else:
            return await message.answer('Доступ запрещен!')
    return wrapped