from aiogram import types, Router, F

from utils.keyboards import excel_kb, admin_kb
from utils.admin_decorator import admin_only


admin_router = Router()


@admin_router.message(F.text == 'Выбрать отчет')
@admin_only
async def get_list_excel_select(message: types.Message, **kwargs):
    await message.answer('Выберите отчет', reply_markup=excel_kb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'Назад')
@admin_only
async def to_main_page(message: types.Message, **kwargs):
    await message.answer('Возврат в главное меню', reply_markup=admin_kb.as_markup(resize_keyboard=True))

