from aiogram import types, Bot, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession


class CurrentEmpoyee(StatesGroup):
    limit = State()
    name = State()

