import asyncio

from aiogram import types, Bot, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import add_answer_to_db, get_all_user_ids
from utils.qiuz_keyboard import quiz_kb
from utils.name_states import response_for_state
from utils.cat_api import get_cat

quiz_router = Router()


pattern = '''
Полиция выгорания с вами на связи
Оцените заеб от 0 до 10

Где 0  - просто эмоциональный вспелеск на ситуацию
Где 10 - откываю фигму с формой и глаза на мокром месте, чувствую отвращение
'''


class Quiz(StatesGroup):
    answer = State()


async def qwe(bot: Bot, storage, session: AsyncSession):
    user_ids = await get_all_user_ids(session)
    # print(user_ids)
    tasks = []
    for user_id in user_ids:
        user_id = user_id[0]
        state = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id,
                           chat_id=user_id,
                           user_id=user_id)
        )
        tasks.append(asyncio.create_task(start_quiz(bot=bot, user_id=user_id, state=state)))

    await asyncio.gather(*tasks)


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
    except Exception:
        await callback.message.answer('Не получилось')
    else:
        await callback.message.answer('Данные отправлены')
        # await callback.message.answer(support_words)
        
        cat_photo = await get_cat(support_words)
        await callback.message.answer_photo(BufferedInputFile(cat_photo,'cat.jpeg'), caption='Лови котика, надеюсь он описывает тебя сейчас😄\nЕсли нет, не принимай близко к сердцу')
        
    await callback.answer()
    await callback.message.delete()