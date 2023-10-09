from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from handlers.main import main_page
from utils.keyboards import create_profile_kb, cancel_kb, create_main_kb
from utils.states import ChangeName
from utils.validate import valid_fullname
from utils.permission_decorators import user_only
from utils.delete_message import try_delete_prev_message, add_message_for_delete
from db.queries import update_fullname, check_user


user_router = Router()


@user_router.message(F.text == 'Профиль')
@user_only
async def profile_settings(message: types.Message,
                           state: FSMContext,
                           session: AsyncSession,
                           bot: Bot,
                           **kwargs):
    await try_delete_prev_message(bot, state)

    profile_kb = await create_profile_kb(message.from_user.id, session)
    msg = await message.answer('Меню профиля',
                               reply_markup=profile_kb.as_markup(resize_keyboard=True),
                               disable_notification=True)
    
    await state.update_data(prev_msg=list())
    data = await state.get_data()

    add_message_for_delete(data, msg)

    await message.delete()


@user_router.message(F.text == 'Изменить имя')
@user_only
async def change_name(message: types.Message,
                      state: FSMContext,
                      session: AsyncSession,
                      bot: Bot,
                      **kwargs):
    await try_delete_prev_message(bot, state)

    user = await check_user(session, message.from_user.id)
    old_name = ' '.join(reversed(user[0].split()))
    await state.update_data(old_name=old_name)

    await start_change_name(message, state)

    await message.delete()


async def start_change_name(message: types.Message,
                            state: FSMContext,
                            retry=None):
    await state.set_state(ChangeName.fullname)

    if retry is None:
        data = await state.get_data()
        old_name = data['old_name']

        msg = await message.answer(f'Ваше имя: {old_name}\nВведите новое имя и фамилию\nПример: Авраам Руссо',
                                   reply_markup=cancel_kb.as_markup(),
                                   disable_notification=True)
    else:
        msg = await message.answer('Некорректный ввод, допускается два слова через пробел, только русские буквы\nПопробуй еще раз\nПример: Авраам Руссо',
                                   reply_markup=cancel_kb.as_markup(),
                                   disable_notification=True)
    
    await state.update_data(prev_msg=list())
    data = await state.get_data()

    add_message_for_delete(data, msg)


@user_router.message(ChangeName.fullname)
async def validate_change_name(message: types.Message,
                               state: FSMContext,
                               session: AsyncSession,
                               bot: Bot,
                               **kwargs):
    await try_delete_prev_message(bot, state)

    if not valid_fullname(message.text):
        await start_change_name(message,
                                state,
                                retry=True)
    else:
        await state.update_data(fullname=message.text.title())
        await state.update_data(user_id=message.from_user.id)

        data = await state.get_data()
        await state.clear()

        try:
            await update_fullname(session, data)
        except Exception:
            msg = await message.answer('Не получилось',
                                       disable_notification=True)
        else:
            profile_kb = await create_profile_kb(message.from_user.id, session)
            msg = await message.answer(f'Имя изменено с <b>{data["old_name"]}</b> на <b>{data["fullname"]}</b>',
                                       reply_markup=profile_kb.as_markup(resize_keyboard=True),
                                       parse_mode='html',
                                       disable_notification=True)

        await state.update_data(prev_msg=list())
        data = await state.get_data()

        add_message_for_delete(data, msg)
    
    await message.delete()


@user_router.callback_query(F.data == 'cancel')
async def cancel_action(callback: types.CallbackQuery,
                        state: FSMContext,
                        bot: Bot):
    text = 'Вернул на главную'

    await main_page(callback,
                    state,
                    bot,
                    text=text)
    # await state.clear()

    # kb = create_main_kb(callback.from_user.id)
    # msg = await callback.message.answer('Вернул на главную',
    #                               reply_markup=kb.as_markup(resize_keyboard=True),
    #                               disable_notification=True)
    
    # await state.update_data(prev_msg=list())
    # data = await state.get_data()

    # add_message_for_delete(data, msg)
    
    # await callback.message.delete()
    

@user_router.message(F.text == 'Вернуться на главную')
@user_only
async def back_to_main(message: types.Message,
                      state: FSMContext,
                      bot: Bot,
                      **kwargs):
    # await try_delete_prev_message(bot, state)

    text = 'Вернул на главную'

    await main_page(message,
                    state,
                    bot,
                    text=text)

    # main_kb = create_main_kb(message.from_user.id)
    # msg = await message.answer('Вернул на главную',
    #                            reply_markup=main_kb.as_markup(resize_keyboard=True),
    #                            disable_notification=True)
    
    # await state.update_data(prev_msg=list())
    # data = await state.get_data()

    # add_message_for_delete(data, msg)

    await message.delete()