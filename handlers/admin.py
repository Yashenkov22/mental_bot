from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from utils.keyboards import excel_kb, create_main_kb, limit_records_kb, create_employee_kb
from utils.permission_decorators import admin_only
from utils.states import CurrentEmpoyee
from handlers.excel import get_excel
from db.queries import current_employee_query, get_all_usernames


admin_router = Router()


@admin_router.message(F.text == 'Выбрать отчет')
@admin_only
async def get_list_excel_select(message: types.Message, **kwargs):
    await message.delete()
    await message.answer('Выберите отчет',
                         reply_markup=excel_kb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'В главное меню')
@admin_only
async def to_main_page(message: types.Message, **kwargs):
    await message.delete()
    main_kb = create_main_kb(message.from_user.id)
    await message.answer('Возврат в главное меню',
                         reply_markup=main_kb.as_markup(resize_keyboard=True))


@admin_router.message(F.text == 'Получить отчет по определённому сотруднику')
@admin_only
async def get_report_for_current_employee(message: types.Message,
                                          state: FSMContext,
                                          session: AsyncSession,
                                          **kwargs):
    list_employees = await get_all_usernames(session)

    if not list_employees:
        await message.answer('В базе ещё нет ни одного сотрудника')
    else:
        await state.update_data(list_employees=list_employees)
        await message.answer('Выберите формат отчета',
                            reply_markup=limit_records_kb.as_markup(resize_keyboard=True))
    
    

@admin_router.message(F.text == 'Назад')
@admin_only
async def to_back(message: types.Message,
                  state: FSMContext,
                  **kwargs):
    await state.clear()
    await get_list_excel_select(message, **kwargs)


@admin_router.message(F.text.contains('Последние'))
@admin_only
async def start_current_employee(message: types.Message,
                                 state: FSMContext,
                                 **kwargs):
    await state.update_data(limit=int(message.text.split()[1]))
    await state.set_state(CurrentEmpoyee.name)

    data = await state.get_data()
    empoyee_kb = create_employee_kb(data['list_employees'])

    await message.answer('Выберите сотрудника', reply_markup=empoyee_kb.as_markup())
    await message.delete()


@admin_router.callback_query(CurrentEmpoyee.name)
@admin_only
async def end_current_employee(callback: types.CallbackQuery,
                               state: FSMContext,
                               session: AsyncSession,
                               engine: AsyncEngine,
                               **kwargs):
    if callback.data == 'back':
        await state.clear()
        await get_report_for_current_employee(callback,
                                              state,
                                              session,
                                              **kwargs)
        await callback.message.delete()
    else:
        await state.update_data(name=callback.data)
        data = await state.get_data()
        stmt = current_employee_query(name=data['name'], limit=data['limit'])
        await get_excel(callback,
                        engine=engine,
                        stmt=stmt,
                        employee_name=data['name'],
                        **kwargs)
