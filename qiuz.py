from aiogram.fsm.state import StatesGroup, State
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from db.queries import add_quiz_answer
from qiuz_keyboard import quiz_kb


quiz_router = Router()

class Quiz(StatesGroup):
    answer = State()


@quiz_router.message(Command('quiz'))
async def qwe(message: types.Message, bot: Bot, state: FSMContext):
    await start_quiz(bot=bot, user_id=message.from_user.id, state=state)


async def start_quiz(bot: Bot,user_id: int, state: FSMContext):
    await state.set_state(Quiz.answer)
    await bot.send_message(user_id, 'Оцени свое состояние', reply_markup=quiz_kb.as_markup())

@quiz_router.message(Quiz.answer)
async def end_quiz(message: types.Message, state: FSMContext, session_maker):
    await state.update_data(answer=int(message.text))
    data = await state.get_data()
    await message.answer(f'Ваше состояние: {data["answer"]}')
    await state.clear()
    success = await add_quiz_answer(session=session_maker, data=data, message=message)
    if success:
        await message.answer('Данные отправлены')
    else:
        await message.answer('Не получилось')