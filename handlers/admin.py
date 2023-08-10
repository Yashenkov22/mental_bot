from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from utils.keyboards import excel_kb, admin_kb, current_employee_kb, create_employee_kb
from utils.admin_decorator import admin_only
from handlers.current_employee import CurrentEmpoyee
from handlers.excel import get_excel
from db.queries import current_employee_query


admin_router = Router()


@admin_router.message(F.text == 'Выбрать отчет')
@admin_only
async def get_list_excel_select(message: types.Message, **kwargs):
    await message.answer('Выберите отчет',
                         reply_markup=excel_kb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'В главное меню')
@admin_only
async def to_main_page(message: types.Message, **kwargs):
    await message.answer('Возврат в главное меню',
                         reply_markup=admin_kb.as_markup(resize_keyboard=True))



@admin_router.message(F.text == 'Получить отчет по определённому сотруднику')
@admin_only
async def get_report_for_current_employee(message: types.Message, **kwargs):
    await message.answer('Выберите формат отчета',
                         reply_markup=current_employee_kb.as_markup(resize_keyboard=True))
    

@admin_router.message(F.text == 'Назад')
@admin_only
async def to_back(message: types.Message, **kwargs):
    await get_list_excel_select(message, **kwargs)


@admin_router.message(F.text.contains('Последние'))
@admin_only
async def start_current_employee(message: types.Message, state: FSMContext, session: AsyncSession, **kwargs):
    # print(kwargs)
    await state.update_data(limit=int(message.text.split()[1]))
    await state.set_state(CurrentEmpoyee.name)
    empoyee_kb = await create_employee_kb(session)
    await message.answer('Выберите сотрудника', reply_markup=empoyee_kb.as_markup())


@admin_router.callback_query(CurrentEmpoyee.name)
async def end_current_employee(callback: types.CallbackQuery,
                               state: FSMContext,
                               engine: AsyncEngine,
                               **kwargs):
    await state.update_data(name=callback.data)
    data = await state.get_data()
    stmt = await current_employee_query(name=data['name'], limit=data['limit'])
    await get_excel(callback,
                    engine=engine,
                    stmt=stmt,
                    **kwargs)
    # print(callback)