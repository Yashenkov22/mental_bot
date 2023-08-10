from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

from sqlalchemy.ext.asyncio import AsyncSession

from db.queries import get_all_usernames


#Inline Keyboard for Quiz
quiz_kb = InlineKeyboardBuilder()
buttons = [types.InlineKeyboardButton(text=str(i),
                                      callback_data=f'answer_{i}') for i in range(11)]
quiz_kb.row(*buttons, width=5)


#Keydoard for Admin
admin_kb = ReplyKeyboardBuilder()
admin_kb.add(types.KeyboardButton(text='Выбрать отчет'))


#Keyboad for select excel file
excel_kb = ReplyKeyboardBuilder()
excel_kb.row(types.KeyboardButton(text='Получить отчет по всем сотрудникам'))
excel_kb.row(types.KeyboardButton(text='Получить отчет по определённому сотруднику'))
excel_kb.row(types.KeyboardButton(text='В главное меню'))

#Keyboard for current employee
current_employee_kb = ReplyKeyboardBuilder()
current_employee_kb.row(types.KeyboardButton(text='Последние 5 записей'))
current_employee_kb.row(types.KeyboardButton(text='Последние 10 записей'))
current_employee_kb.row(types.KeyboardButton(text='Назад'))


#Inline keyboard employees
async def create_employee_kb(session: AsyncSession):
    employees_kb = InlineKeyboardBuilder()
    emloyee_names = await get_all_usernames(session)
    for name in emloyee_names:
        employees_kb.row(types.InlineKeyboardButton(text=name[0],
                                                    callback_data=name[0]))
    return employees_kb
