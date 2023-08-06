from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ScalarResult
from sqlalchemy import select
from aiogram import types

from db.models import User, MentalState


async def check_user(session: AsyncSession, user_id: int):
    async with session() as session:
        async with session.begin():
            session: AsyncSession
            result = await session.execute(select(User).where(User.user_id == user_id))
            result: ScalarResult
            user = result.one_or_none()
            return user


async def register_user(session: AsyncSession, data: dict, message: types.Message):
    success = False
    # async with session() as session:
    async with session.begin():
        session: AsyncSession
        session.add(User(user_id=message.from_user.id,
                                username=message.from_user.username,
                                fullname=data['first_name'] + ' ' + data['last_name']))
        success = True
    return success


async def add_quiz_answer(session: AsyncSession, data: dict, message: types.Message):
    success = False
    async with session() as session:
        async with session.begin():
            session: AsyncSession
            session.add(MentalState(user_id=message.from_user.id,
                                    state=data['answer']))
        success = True
    return success