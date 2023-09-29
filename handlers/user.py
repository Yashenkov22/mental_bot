from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from utils.keyboards import create_profile_kb, cancel_kb, create_main_kb
from utils.states import ChangeName
from utils.validate import valid_fullname
from utils.permission_decorators import user_only
from db.queries import update_fullname, check_user


user_router = Router()


@user_router.message(F.text == 'Профиль')
@user_only
async def profile_settings(message: types.Message,
                           session: AsyncSession,
                           **kwargs):
    profile_kb = await create_profile_kb(message.from_user.id, session)
    await message.answer('Меню профиля', reply_markup=profile_kb.as_markup(resize_keyboard=True))
    await message.delete()


@user_router.message(F.text == 'Изменить имя')
@user_only
async def change_name(message: types.Message,
                      state: FSMContext,
                      session: AsyncSession,
                      **kwargs):
    data = await state.get_data()
    old_name = data.get('old_name')

    if old_name is None:
        user = await check_user(session, message.from_user.id)
        old_name = ' '.join(reversed(user[0].split()))
        await state.update_data(old_name=old_name)
        await state.set_state(ChangeName.fullname)

    await message.answer(f'Ваше имя: {old_name}\nВведите новое имя и фамилию\nПример: Авраам Руссо',
                         reply_markup=cancel_kb.as_markup())


@user_router.message(ChangeName.fullname)
async def validate_change_name(message: types.Message,
                               state: FSMContext,
                               session: AsyncSession):
    if not valid_fullname(message.text):
        await message.answer('Некорректный ввод, допускается два слова через пробел, только русские буквы\nПопробуй еще раз')
        await change_name(message, state)
    else:
        await state.update_data(fullname=message.text.title())
        await state.update_data(user_id=message.from_user.id)

        data = await state.get_data()
        await state.clear()

        try:
            await update_fullname(session, data)
        except Exception:
            await message.answer('Не получилось')
        else:
            profile_kb = await create_profile_kb(message.from_user.id, session)
            await message.answer(f'Имя изменено с <b>{data["old_name"]}</b> на <b>{data["fullname"]}</b>',
                                 reply_markup=profile_kb.as_markup(resize_keyboard=True),
                                 parse_mode='html')


@user_router.callback_query(F.data == 'cancel')
async def cancel_action(callback: types.CallbackQuery,
                        state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.delete()
    

@user_router.message(F.text == 'Вернуться на главную')
@user_only
async def change_name(message: types.Message, **kwargs):
    main_kb = create_main_kb(message.from_user.id)
    await message.answer('Вернул на главную',
                         reply_markup=main_kb.as_markup(resize_keyboard=True))
    await message.delete()