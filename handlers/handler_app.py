import os
from datetime import datetime

import pandas as pd
from aiogram import types
from aiogram import Router
from aiogram.types import FSInputFile
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncEngine

from db.queries import all_result_query


any_router = Router()


def read_sql_query(con, stmt):
    return pd.read_sql_query(stmt, con)


@any_router.message(Command('pand'))
async def get_excel(message: types.Message, engine: AsyncEngine):
    async with engine.begin() as conn:
        df_sql = await conn.run_sync(read_sql_query, all_result_query)
        df_sql = df_sql.astype({'date': str})

    filename = str(datetime.now()) + '.xlsx'
    df_sql.to_excel(filename)

    await message.reply_document(FSInputFile(filename))

    if os.path.isfile(filename):
        os.remove(filename)

    # print(df_sql['date'])


@any_router.message()
async def any_input(message: types.Message):
    await message.answer('Бот не принимает произвольные сообщения\nБот обрабатывает только отправленные им же опросы')
