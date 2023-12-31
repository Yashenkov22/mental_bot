import os
from datetime import datetime
from typing import Union

import pandas as pd
from aiogram import types, Router, F
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import AsyncEngine

from utils.admin_decorator import admin_only
from db.queries import all_result_query


excel_router = Router()


def read_sql_query(con, stmt):
    return pd.read_sql_query(stmt, con)


@excel_router.message(F.text == 'Получить отчет по всем сотрудникам')
@admin_only
async def get_excel(message: Union[types.Message, types.CallbackQuery],
                    engine: AsyncEngine,
                    stmt=all_result_query,
                    **kwargs):
    
    async with engine.begin() as conn:
        df_sql = await conn.run_sync(read_sql_query, stmt)
        df_sql = df_sql.astype({'date': str})

    if df_sql.empty:
        if isinstance(message, types.Message):
            await message.answer('В базе пока нет данных о состоянии сотрудников')
        else:
            await message.answer('В базе пока нет данных о состоянии выбранного сотрудника')
    
    else:
        filename = str(datetime.now()) + '.xlsx'
        df_sql.to_excel(filename)
        
        if isinstance(message, types.CallbackQuery):
            message = message.message
 
        await message.answer_document(FSInputFile(filename))
        await message.delete()

        if os.path.isfile(filename):
            os.remove(filename)


@excel_router.message()
async def any_input(message: types.Message):
    await message.answer('Бот не принимает произвольные сообщения\nБот обрабатывает только отправленные им же опросы')
