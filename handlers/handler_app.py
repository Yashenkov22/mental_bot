from aiogram import types
from aiogram import Router
from aiogram.filters import Command
import pandas as pd
from db.queries import all_result_query
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine import create_engine
from config import db_url

# engine = create_engine(db_url)

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
async def get_excel(message: types.Message, engine: AsyncEngine):
    async with engine.begin() as conn:
        data = await conn.run_sync(read_sql_query, all_result_query)
    print(data)


@any_router.message()
async def any_input(message: types.Message):
    await message.answer('Бот не принимает произвольные сообщения\nБот обрабатывает только отправленные им же опросы')
