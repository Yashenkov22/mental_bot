from aiogram import types, Router, F

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import update_current_subscribe
from utils.keyboards import create_profile_kb
from utils.permission_decorators import user_only

subscribe_router = Router()


@subscribe_router.message(F.text.endswith('рассылку'))
@user_only
async def switch_subscribe(message: types.Message,
                           session: AsyncSession,
                           **kwargs):
    user_id = message.from_user.id
    new_subscribe = await update_current_subscribe(user_id, session)
    
    ans_text = 'включена' if new_subscribe else 'отключена'

    profile_kb = await create_profile_kb(user_id, session)

    await message.answer(f'Рассылка {ans_text}',
                         reply_markup=profile_kb.as_markup(resize_keyboard=True))
    
    await message.delete()