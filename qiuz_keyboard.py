from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


quiz_kb = InlineKeyboardBuilder()

buttons = [types.InlineKeyboardButton(text=str(i),callback_data='answer_{i}') for i in range(11)]

quiz_kb.row(*buttons, width=5)

