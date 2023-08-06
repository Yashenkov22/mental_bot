import asyncio

from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from db.queries import add_quiz_answer, get_all_user_ids
from qiuz_keyboard import quiz_kb
from aiogram import F
from aiogram.fsm.storage.base import StorageKey

quiz_router = Router()

class Quiz(StatesGroup):
    answer = State()



async def qwe(bot: Bot, storage, session_maker):
    user_ids = await get_all_user_ids(session_maker)
    print(user_ids)
    tasks = []
    for user_id in user_ids:
        user_id = user_id[0]
        state: FSMContext = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id,
                           chat_id=user_id,
                           user_id=user_id)
        )
        tasks.append(asyncio.create_task(start_quiz(bot=bot, user_id=user_id, state=state)))
    # tasks = [asyncio.create_task(start_quiz(bot=bot, user_id=user_id, state=state)) for user_id in user_ids]
    # for task in tasks:
    #     await task
    await asyncio.gather(*tasks)


async def start_quiz(bot: Bot,user_id: int, state: FSMContext):
    await state.set_state(Quiz.answer)
    await bot.send_message(user_id, 'Оцени свое состояние', reply_markup=quiz_kb.as_markup())


@quiz_router.callback_query(Quiz.answer)
async def end_quiz(callback: types.CallbackQuery, state: FSMContext, session_maker):
    answer = callback.data.split('_')[-1]
    await state.update_data(answer=int(answer))
    data = await state.get_data()
    await callback.message.answer(f'Ваше состояние: {data["answer"]}')
    await state.clear()
    
    success = await add_quiz_answer(session=session_maker, data=data, user_id=callback.from_user.id)
    if success:
        await callback.message.answer('Данные отправлены')
    else:
        await callback.message.answer('Не получилось')
    await callback.answer()
    await callback.message.delete()