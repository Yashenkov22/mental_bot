from aiogram import types, Router, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import register_user, check_user
from handlers.qiuz import start_quiz
from utils.keyboards import admin_kb
from utils.states import RegisterUser
from utils.register_valudate import valid_fullname
from config import ADMIN_ID


register_router = Router()



@register_router.message(Command('start'))
async def start(message: types.Message, session: AsyncSession, state: FSMContext):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer('Вы админ этого бота', reply_markup=admin_kb.as_markup(resize_keyboard=True))
    else:
        check = await check_user(session=session, user_id=message.from_user.id)
        if check:
            await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nТы уже все знаешь.')
        else:
            await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nЕсли серьезно, я буду следить за Вашим ментальным состоянием\nДля начала давай познакомимся.')
            await start_register(message, state)
        await message.delete()


async def start_register(message: types.Message, state: FSMContext):
            await state.set_state(RegisterUser.fullname)
            await message.answer('Введи своё имя и фамилию\nПример: Авраам Руссо')


@register_router.message(RegisterUser.fullname)
async def end_register(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await state.update_data(fullname=message.text.title())
    data = await state.get_data()

    if not valid_fullname(data['fullname']):
         await state.clear()
         await message.answer('Некорректный ввод, допускается два слова через пробел, только русские буквы\nПопробуй еще раз')
         await start_register(message, state)

    else:     
        await message.answer(f'Приятно познакомиться, {data["fullname"]}')
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

