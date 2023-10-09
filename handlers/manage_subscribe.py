from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import update_current_subscribe
from utils.keyboards import create_profile_kb
from utils.permission_decorators import user_only
from utils.delete_message import try_delete_prev_message, add_message_for_delete

subscribe_router = Router()


@subscribe_router.message(F.text.endswith('рассылку'))
@user_only
async def switch_subscribe(message: types.Message,
                           state: FSMContext,
                           session: AsyncSession,
                           bot: Bot,
                           **kwargs):
    await try_delete_prev_message(bot, state)

    user_id = message.from_user.id
    new_subscribe = await update_current_subscribe(user_id, session)
    
    ans_text = 'включена' if new_subscribe else 'отключена'

    profile_kb = await create_profile_kb(user_id, session)

    msg = await message.answer(f'Рассылка {ans_text}',
                               reply_markup=profile_kb.as_markup(resize_keyboard=True),
                               disable_notification=True)
    
    await state.update_data(prev_msg=list())
    data = await state.get_data()

    add_message_for_delete(data, msg)   
    
    await message.delete()