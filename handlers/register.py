from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import register_user, check_user
from handlers.main import main_page
from handlers.qiuz import start_quiz
from config import ADMIN_IDS, SECRET_WORD
from utils.states import RegisterUser, ValidateUser
from utils.validate import valid_fullname
from utils.delete_message import try_delete_prev_message, add_message_for_delete


register_router = Router()

register_answer = '''
Приятно познакомиться,

Периодически я буду узнавать у Вас об уровне Вашего выгорания, чтобы понять, когда Вас тушить🧯
'''

#Start command
@register_router.message(Command('start'))
async def start(message: types.Message,
                state: FSMContext,
                session: AsyncSession,
                bot: Bot):

    if message.from_user.id in ADMIN_IDS:
        await main_page(message,
                        state,
                        bot,
                        text='Привет, Босс')
    else:
        check = await check_user(session=session, user_id=message.from_user.id)
        
        if check:
            text = 'Привет, это Полиция Выгорания, руки на копот😁\nТы уже все знаешь.'
            await main_page(message,
                            state,
                            bot,
                            text=text)
        else:
            await validate_user(message, state, bot)

    await message.delete()


#Validate on start
async def validate_user(message: types.Message,
                        state: FSMContext,
                        bot: Bot,
                        retry=None):

    await try_delete_prev_message(bot, state)

    await state.set_state(ValidateUser.secret_word)

    text = 'Введи секретное слово...' if retry is None else 'Хм..Это не то слово, попробуй еще раз'

    msg = await message.answer(text,
                               disable_notification=True)

    await state.update_data(secret=msg)


@register_router.message(ValidateUser.secret_word)
async def end_validate_user(message: types.Message,
                            state: FSMContext,
                            bot: Bot):
    d = await state.get_data()
    secret = d['secret']
    await bot.delete_message(secret.chat.id, secret.message_id)

    if message.text.lower() == SECRET_WORD:
        await state.clear()
        msg = await message.answer(f'Привет, это Полиция Выгорания, руки на копот😁\nЕсли серьезно, я буду следить за Вашим ментальным состоянием\nДля начала давай познакомимся.',
                                   disable_notification=True)
        
        await state.update_data(prev_msg=list())
        data = await state.get_data()

        add_message_for_delete(data, msg)
        
        await start_register(message, state, bot)
    else:
        await validate_user(message,
                            state,
                            bot,
                            retry=True)
    
    await message.delete()


#Register on start
async def start_register(message: types.Message,
                         state: FSMContext,
                         bot: Bot,
                         retry=None):
    await state.set_state(RegisterUser.fullname)

    d = await state.get_data()

    input_name = d.get('input_name')

    if input_name:
        await bot.delete_message(input_name.chat.id, input_name.message_id)

    text = 'Введи своё имя и фамилию\nПример: Авраам Руссо' if retry is None else 'Некорректный ввод, допускается два слова через пробел, только русские буквы\nПопробуй еще раз'

    msg = await message.answer(text,
                               disable_notification=True)

    await state.update_data(input_name=msg)


@register_router.message(RegisterUser.fullname)
async def end_register(message: types.Message,
                       state: FSMContext, 
                       session: AsyncSession,
                       bot: Bot):
    fullname = message.text.title()
    data = await state.get_data()
    
    if not valid_fullname(fullname):
        await start_register(message, state, bot, retry=True)

    else:
        msg = None

        try:
            await register_user(session=session, fullname=fullname, message=message)
        except Exception:
            msg = await message.answer('Ошибка регистрации',
                                       disable_notification=True)
        else:
            await message.answer(register_answer,
                                 disable_notification=True)
            first_quiz = await message.answer('Давай сразу и попробуем',
                                       disable_notification=True)

            await state.update_data(first_quiz=first_quiz)

            await start_quiz(bot, message.from_user.id, state=state)

        input_name = data.get('input_name')

        if input_name:
            await bot.delete_message(input_name.chat.id, input_name.message_id)

        add_message_for_delete(data, msg)

    await message.delete()