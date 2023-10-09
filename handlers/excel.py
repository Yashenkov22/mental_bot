import os
from datetime import date
from typing import Union

import pandas as pd

from aiogram import types, Router, F, Bot
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncEngine

from handlers.main import main_page
from utils.permission_decorators import admin_only
from utils.keyboards import create_main_kb
from utils.delete_message import try_delete_prev_message
from db.queries import all_result_query


excel_router = Router()


def read_sql_query(con, stmt):
    return pd.read_sql_query(stmt, con)


@excel_router.message(F.text == 'Получить отчет по всем сотрудникам')
@admin_only
async def get_excel(message: Union[types.Message, types.CallbackQuery],
                    engine: AsyncEngine,
                    state: FSMContext,
                    bot: Bot,
                    stmt=all_result_query,
                    employee_name=None,
                    **kwargs):
    await try_delete_prev_message(bot, state)
    
    async with engine.begin() as conn:
        df_sql = await conn.run_sync(read_sql_query, stmt)
        df_sql = df_sql.astype({'date': str})

    if df_sql.empty:

        if isinstance(message, types.Message):
            text = 'В базе пока нет данных о состоянии сотрудников'
            await main_page(message,
                            state,
                            bot,
                            text=text)
        else:
            await message.answer('В базе пока нет данных о состоянии выбранного сотрудника')
    
    else:
        subname_file: str

        if isinstance(message, types.Message):
            subname_file = 'Отчет по всем сотрудникам'
        else:
            subname_file = f'Отчет по сотруднику {employee_name}'

        filename = subname_file + ' ' + str(date.today()) + '.xlsx'

        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        sheetname = 'Все сотрудники' if employee_name is None else employee_name

        df_sql.to_excel(writer,
                        sheet_name=sheetname,
                        index=False,
                        header=['Имя',
                                'Дата',
                                'Степень выгорания'])

        worksheet = writer.sheets[sheetname]
        worksheet.set_column(0,0, 22)
        worksheet.set_column(1,1, 11)
        worksheet.set_column(2,2, 18)

        writer.close()

        kb = create_main_kb(message.from_user.id)
        
        if isinstance(message, types.CallbackQuery):
            message = message.message

        await message.answer_document(FSInputFile(filename),
                                      reply_markup=kb.as_markup(resize_keyboard=True))

        if os.path.isfile(filename):
            os.remove(filename)
    
    await message.delete()


