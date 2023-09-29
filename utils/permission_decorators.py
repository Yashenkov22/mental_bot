from aiogram import types
from config import ADMIN_IDS

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import check_user


def admin_only(func):
    async def wrapped(*args, **kwargs):
        message = None
        for arg in args:
            if isinstance(arg, (types.Message, types.CallbackQuery)):
                message = arg
                break
        if message.from_user.id in ADMIN_IDS:
            return await func(*args, **kwargs)
        else:
            return await message.answer('Доступ запрещен!')
    return wrapped


def user_only(func):
    async def wrapped(*args, **kwargs):
        message: types.Message
        session: AsyncSession

        for arg in args:
            if isinstance(arg, types.Message):
                message = arg 

        session = kwargs['session'] 
        user = await check_user(session, message.from_user.id)

        if user:
            return await func(*args, **kwargs)
        else:
            return await message.answer('Доступ запрещен!')
    return wrapped