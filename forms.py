from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from db.queries import register_user
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries import check_user


form_router = Router()


class Form(StatesGroup):
    first_name: str = State()
    last_name: str = State()


@form_router.message(Command('start'))
async def start(message: types.Message, session_maker, state: FSMContext = None):
    check = await check_user(session=session_maker, user_id=message.from_user.id)
    if check:
        await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nТы уже все знаешь.')
        await message.answer(str(message.chat.id))
    else:
        await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nЕсли серьезно, я буду следить за Вашим ментальным состоянием\nДля начала давай познакомимся.')

        await state.set_state(Form.first_name)
        await message.answer('Введи своё имя')
    await message.delete()


@form_router.message(Form.first_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.capitalize())
    await message.answer(f'Твое имя {message.text.capitalize()}.\nТеперь введи свою фамилия')
    await state.set_state(Form.last_name)


@form_router.message(Form.last_name)
async def process_last_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(last_name=message.text.capitalize())
    data = await state.get_data()
    await message.answer(f'Ваше имя: {data["first_name"]} {data["last_name"]}')
    await state.clear()
    success = await register_user(session=session, data=data, message=message)
    if success:
        await message.answer('Вы зарегистрировались')
    else:
        await message.answer('Не получилось')
        

