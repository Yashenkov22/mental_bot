from aiogram import types, Bot, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import add_answer_to_db
from utils.keyboards import quiz_kb
from utils.states import Quiz
from utils.name_states import response_for_state
from utils.cat_api import get_cat


quiz_router = Router()


pattern = '''
Полиция выгорания с вами на связи
Оцените заеб от 0 до 10

Где 0  - просто эмоциональный вспелеск на ситуацию
Где 10 - откываю фигму с формой и глаза на мокром месте, чувствую отвращение
'''



async def start_quiz(bot: Bot, user_id: int, state: FSMContext):
    await state.set_state(Quiz.answer)
    await bot.send_message(user_id, pattern, reply_markup=quiz_kb.as_markup())


@quiz_router.callback_query(Quiz.answer)
async def end_quiz(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    
    answer = callback.data.split('_')[-1]
    await state.update_data(answer=int(answer))
    data = await state.get_data()

    support_words = response_for_state(answer)

    await state.clear()
    
    try:
        await add_answer_to_db(session=session, data=data, user_id=callback.from_user.id)
    except Exception as ex:
        print(ex)
        await callback.message.answer('Не получилось')
    else:
        await callback.message.answer('Данные отправлены')
        # await callback.message.answer(support_words)
        
        cat_photo = await get_cat(support_words)
        await callback.message.answer_photo(BufferedInputFile(cat_photo, 'cat.jpeg'),
                                            caption='Лови котика, надеюсь он описывает тебя сейчас😄\nЕсли нет, не принимай близко к сердцу, я всего лишь бот, но я стараюсь')
        
    await callback.answer()
    await callback.message.delete()