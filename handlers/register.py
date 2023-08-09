from aiogram import types, Router, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import register_user, check_user
from handlers.qiuz import start_quiz
from utils.keyboards import admin_kb
from config import ADMIN_ID



register_router = Router()


class Form(StatesGroup):
    first_name: str = State()
    last_name: str = State()


@register_router.message(Command('start'))
async def start_register(message: types.Message, session: AsyncSession, state: FSMContext):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer('Вы админ этого бота', reply_markup=admin_kb.as_markup(resize_keyboard=True))
    # await message.answer(str(message.from_user.id))
    else:
        check = await check_user(session=session, user_id=message.from_user.id)
        if check:
            await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nТы уже все знаешь.')
        else:
            await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nЕсли серьезно, я буду следить за Вашим ментальным состоянием\nДля начала давай познакомимся.')

            await state.set_state(Form.first_name)
            await message.answer('Введи своё имя (только имя)')
        await message.delete()


@register_router.message(Form.first_name)
async def process_register(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.capitalize())
    await message.answer(f'Привет, {message.text.capitalize()}.\nТеперь введи свою фамилия')
    await state.set_state(Form.last_name)


@register_router.message(Form.last_name)
async def end_register(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await state.update_data(last_name=message.text.capitalize())
    data = await state.get_data()
    await message.answer(f'Приятно познакомиться, {data["first_name"]} {data["last_name"]}')
    await state.clear()
    try:
        await register_user(session=session, data=data, message=message)
    except Exception:
        await message.answer('Ошибка регистрации')
    else:
        await message.answer('Вы зарегистрировались')
        await message.answer('Периодически я буду узнавать у Вас об уровне Вашего выгорания, чтобы понять, когда Вас тушить🧯')
        await message.answer('Давай сразу и попробуем')
        await start_quiz(bot, message.from_user.id, state=state)

