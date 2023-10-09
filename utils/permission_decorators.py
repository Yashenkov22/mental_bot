from aiogram import types
from config import ADMIN_IDS

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import check_user
from .delete_message import add_message_for_delete


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
            state = kwargs['state']
            msg = await message.answer('Доступ запрещен!')
            data = await state.get_data()
            add_message_for_delete(data, msg)

            await message.delete()
            return msg
    return wrapped


def user_only(func):
    async def wrapped(*args, **kwargs):
        message: types.Message
        session: AsyncSession

        for arg in args:
            if isinstance(arg, types.Message):
                message = arg
                break
        
        session = kwargs['session']

        user = await check_user(session, message.from_user.id)

        if user:
            return await func(*args, **kwargs)
        else:
            state = kwargs['state']
            msg = await message.answer('Доступ запрещен!')
            data = await state.get_data()
            add_message_for_delete(data, msg)

            await message.delete()
            return msg
    return wrapped