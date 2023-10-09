from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import get_all_usernames, get_current_subscribe
from config import ADMIN_IDS


#Inline Keyboard for Quiz
quiz_kb = InlineKeyboardBuilder()
buttons = [types.InlineKeyboardButton(text=str(i),
                                      callback_data=f'answer_{i}') for i in range(11)]
quiz_kb.row(*buttons, width=5)


def create_main_kb(user_id):
    main_kb = ReplyKeyboardBuilder()
    btn_name: str

    if user_id in ADMIN_IDS:
        btn_name = 'Выбрать отчет'
    else:
        btn_name = 'Профиль'

    main_kb.row(types.KeyboardButton(text=btn_name))

    return main_kb


#Profile keydoard for user
async def create_profile_kb(user_id: int, session: AsyncSession):
    profile_kb = ReplyKeyboardBuilder()

    current_subscribe: bool
    current_subscribe = await get_current_subscribe(user_id, session)
    
    btn_subname = 'Включить'

    if current_subscribe is not None:
        subscribe = current_subscribe[0]
        if subscribe:
            btn_subname = 'Отключить'

    btn_name = f'{btn_subname} рассылку'

    profile_kb.row(types.KeyboardButton(text=btn_name))
    profile_kb.row(types.KeyboardButton(text='Изменить имя'))
    profile_kb.row(types.KeyboardButton(text='Вернуться на главную'))

    return profile_kb


#Keyboad for select excel file
excel_kb = ReplyKeyboardBuilder()
excel_kb.row(types.KeyboardButton(text='Получить отчет по всем сотрудникам'))
excel_kb.row(types.KeyboardButton(text='Получить отчет по определённому сотруднику'))
excel_kb.row(types.KeyboardButton(text='В главное меню'))

#Keyboard for current employee
limit_records_kb = ReplyKeyboardBuilder()
limit_records_kb.row(types.KeyboardButton(text='Последние 5 записей'))
limit_records_kb.row(types.KeyboardButton(text='Последние 10 записей'))
limit_records_kb.row(types.KeyboardButton(text='Назад'))


#Inline keyboard employees
def create_employee_kb(employees_list: list):
    employees_kb = InlineKeyboardBuilder()

    for name in employees_list:
        employees_kb.row(types.InlineKeyboardButton(text=name[0],
                                                    callback_data=name[0]))
    employees_kb.row(types.InlineKeyboardButton(text='Назад',
                                                callback_data='back'))
    return employees_kb


#Inline cancel keyboard
cancel_kb = InlineKeyboardBuilder()
cancel_btn = types.InlineKeyboardButton(text='Отмена действия',
                                        callback_data='cancel')
cancel_kb.row(cancel_btn)