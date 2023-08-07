import os
import pandas as pd
from time import sleep
from aiogram import types, Bot
from aiogram import Router
from aiogram.filters import Command
from db.queries import all_result_query
from sqlalchemy.ext.asyncio import AsyncEngine
from datetime import date
from aiogram.types import FSInputFile


pattern = '''
Полиция выгорания с вами на связи
Оцените заеб от 0 до 10

Где 0  - просто эмоциональный вспелеск на ситуацию
Где 10 - откываю фигму с формой и глаза на мокром месте, чувствую отвращение
'''

any_router = Router()

def read_sql_query(con, stmt):
    return pd.read_sql_query(stmt, con)

@any_router.message(Command('pand'))
async def get_excel(message: types.Message, engine: AsyncEngine, bot: Bot):
    async with engine.begin() as conn:
        data = await conn.run_sync(read_sql_query, all_result_query)
        data = data.astype({'date': str})
    filename = str(date.today()) + '.xlsx'
    data.to_excel(filename)
    await message.reply_document(FSInputFile(filename))
    if os.path.isfile(filename):
        os.remove(filename)
    print(data['date'])


@any_router.message()
async def any_input(message: types.Message):
    await message.answer('Бот не принимает произвольные сообщения\nБот обрабатывает только отправленные им же опросы')
