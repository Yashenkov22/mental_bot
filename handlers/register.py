from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import register_user, check_user
from handlers.qiuz import start_quiz
from config import ADMIN_IDS, SECRET_WORD
from utils.keyboards import create_main_kb
from utils.states import RegisterUser, ValidateUser
from utils.validate import valid_fullname
from utils.delete_message import try_delete_prev_message, add_message_for_delete


register_router = Router()

register_answer = '''
Вы зарегистрировались

Периодически я буду узнавать у Вас об уровне Вашего выгорания, чтобы понять, когда Вас тушить🧯

Давай сразу и попробуем
'''

#Validate on start
async def validate_user(message: types.Message, state: FSMContext):
     await state.set_state(ValidateUser.secret_word)
     await message.answer('Введи секретное слово...')

@register_router.message(ValidateUser.secret_word)
async def end_validate_user(message: types.Message, state: FSMContext):
    if message.text.lower() == SECRET_WORD:
        await state.clear()
        await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nЕсли серьезно, я буду следить за Вашим ментальным состоянием\nДля начала давай познакомимся.')
        await start_register(message, state)
    else:
        await message.answer('Хм..Это не то слово, попробуй еще раз')
        await validate_user(message, state)


#Start command
@register_router.message(Command('start'))
async def start(message: types.Message, session: AsyncSession, state: FSMContext):
    
    main_kb = create_main_kb(message.from_user.id)

    if message.from_user.id in ADMIN_IDS:
        msg = await message.answer('Привет, Босс',
                             reply_markup=main_kb.as_markup(resize_keyboard=True))
    else:
        check = await check_user(session=session, user_id=message.from_user.id)
        
        if check:
            msg = await message.answer(f'Привет {message.from_user.full_name}, это Полиция Выгорания, руки на копот😁\nТы уже все знаешь.',
                                 reply_markup=main_kb.as_markup(resize_keyboard=True))
        else:
            await validate_user(message, state)

    # await state.update_data(prev_msg=list())
    # data = await state.get_data()

    # add_message_for_delete(data, msg)

    await message.delete()


#Register on start
async def start_register(message: types.Message, state: FSMContext):
            await state.set_state(RegisterUser.fullname)
            await message.answer('Введи своё имя и фамилию\nПример: Авраам Руссо')


@register_router.message(RegisterUser.fullname)
async def end_register(message: types.Message,
                       state: FSMContext, 
                       session: AsyncSession,
                       bot: Bot):
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
            await message.answer(register_answer)
            await start_quiz(bot, message.from_user.id, state=state)