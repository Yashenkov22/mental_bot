from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

#Inline Keyboard for Quiz
quiz_kb = InlineKeyboardBuilder()
buttons = [types.InlineKeyboardButton(text=str(i),callback_data=f'answer_{i}') for i in range(11)]
quiz_kb.row(*buttons, width=5)


#Keydoard for Admin
admin_kb = ReplyKeyboardBuilder()
admin_kb.add(types.KeyboardButton(text='Выбрать отчет'))

excel_kb = ReplyKeyboardBuilder()
excel_kb.row(types.KeyboardButton(text='Получить отчет по всем сотрудникам'))
excel_kb.row(types.KeyboardButton(text='Назад'))
# excel_kb.add(types.KeyboardButton(text='Получить отчет по всем сотрудникам'))