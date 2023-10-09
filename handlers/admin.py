from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from handlers.main import main_page
from utils.keyboards import excel_kb, limit_records_kb, create_employee_kb
from utils.permission_decorators import admin_only
from utils.states import CurrentEmpoyee
from utils.delete_message import try_delete_prev_message, add_message_for_delete
from handlers.excel import get_excel
from db.queries import current_employee_query, get_all_usernames


admin_router = Router()


@admin_router.message(F.text == 'Выбрать отчет')
@admin_only
async def get_list_excel_select(message: types.Message,
                                state: FSMContext,
                                bot: Bot,
                                **kwargs):
    await try_delete_prev_message(bot, state)

    msg = await message.answer('Выберите отчет',
                         reply_markup=excel_kb.as_markup(resize_keyboard=True),
                         disable_notification=True)
    
    await state.update_data(prev_msg=list())
    data = await state.get_data()

    add_message_for_delete(data, msg)

    try:
        await message.delete()
    except TelegramBadRequest:
        pass


@admin_router.message(F.text == 'В главное меню')
@admin_only
async def to_main_page(message: types.Message,
                       state: FSMContext,
                       bot: Bot,
                       **kwargs):
    text = 'Вернул на главную, Босс'

    await main_page(message,
                    state,
                    bot,
                    text=text)

    await message.delete()


@admin_router.message(F.text == 'Получить отчет по определённому сотруднику')
@admin_only
async def get_report_for_current_employee(message: types.Message,
                                          state: FSMContext,
                                          session: AsyncSession,
                                          bot: Bot,
                                          **kwargs):
    await try_delete_prev_message(bot, state)

    list_employees = await get_all_usernames(session)

    if isinstance(message, types.CallbackQuery):
        message = message.message

    if not list_employees:
        text = 'В базе ещё нет ни одного сотрудника'
        await main_page(message,
                        state,
                        bot,
                        text=text)
    else:
        await state.update_data(list_employees=list_employees)
        msg = await message.answer('Выберите формат отчета',
                            reply_markup=limit_records_kb.as_markup(resize_keyboard=True))
    
        await state.update_data(prev_msg=list())
        data = await state.get_data()

        add_message_for_delete(data, msg)

    try:  
        await message.delete()
    except TelegramBadRequest:
        pass


@admin_router.message(F.text == 'Назад')
@admin_only
async def to_back(message: types.Message,
                  state: FSMContext,
                  bot: Bot,
                  **kwargs):
    await get_list_excel_select(message,
                                state,
                                bot,
                                **kwargs)


@admin_router.message(F.text.contains('Последние'))
@admin_only
async def start_current_employee(message: types.Message,
                                 state: FSMContext,
                                 bot: Bot,
                                 **kwargs):
    await try_delete_prev_message(bot, state)

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
                               bot: Bot,
                               **kwargs):
    if callback.data == 'back':
        await state.clear()
        await get_report_for_current_employee(callback,
                                              state,
                                              session,
                                              **kwargs)
    else:
        await state.update_data(name=callback.data)
        data = await state.get_data()
        stmt = current_employee_query(name=data['name'], limit=data['limit'])
        await get_excel(callback,
                        engine=engine,
                        state=state,
                        stmt=stmt,
                        bot=bot,
                        employee_name=data['name'],
                        **kwargs)
