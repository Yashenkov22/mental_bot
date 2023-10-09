from aiogram import types, Router, Bot
from aiogram.fsm.context import FSMContext

from utils.delete_message import try_delete_prev_message, add_message_for_delete
from utils.keyboards import create_main_kb


main_router = Router()


async def main_page(message: types.Message | types.CallbackQuery,
                    state: FSMContext,
                    bot: Bot,
                    text='Главное меню'):
    await try_delete_prev_message(bot, state)

    # await state.clear()

    kb = create_main_kb(message.from_user.id)

    if isinstance(message, types.CallbackQuery):
        message = message.message

    msg = await message.answer(text,
                               reply_markup=kb.as_markup(resize_keyboard=True),
                               disable_notification=True)
    
    await state.update_data(prev_msg=list())
    data = await state.get_data()

    add_message_for_delete(data, msg)


@main_router.message()
async def any_input(message: types.Message,
                    state: FSMContext,
                    bot: Bot):
    text = 'Бот не принимает произвольные сообщения'

    await main_page(message,
                    state,
                    bot,
                    text=text)

    await message.delete()