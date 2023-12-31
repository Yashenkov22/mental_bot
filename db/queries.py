from aiogram import types

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.engine import ScalarResult
from sqlalchemy import select

from db.models import User, MentalState


all_result_query = '''
    SELECT u.fullname, date, state
    FROM users u
    JOIN states s on u.user_id = s.user_id
    ORDER BY date DESC, u.fullname
'''

def current_employee_query(name, limit):
    query = f'''
    SELECT u.fullname, date, state
    FROM users u
    JOIN states s on u.user_id = s.user_id
    WHERE u.fullname = '{name}'
    ORDER BY date DESC
    LIMIT {limit}
    '''
    return query
      


async def check_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.user_id == user_id))
    result: ScalarResult
    user = result.one_or_none()
    return user


async def register_user(session: AsyncSession, data: dict[str,str], message: types.Message):
    fullname = ' '.join(reversed(data['fullname'].split()))
    async with session.begin():
        session: AsyncSession
        session.add(User(user_id=message.from_user.id,
                        fullname=fullname))


async def add_answer_to_db(session: AsyncSession, data: dict, user_id: int):
    async with session.begin():
        session: AsyncSession
        session.add(MentalState(user_id=user_id,
                                state=data['answer']))


async def get_all_user_ids(session: async_sessionmaker):
    async with session() as session:
        session: AsyncSession
        user_ids = await session.execute(select(User.user_id))
        user_ids: ScalarResult
        return user_ids.all()
    

async def get_all_usernames(session: AsyncSession):
    result = await session.execute(select(User.fullname).order_by(User.fullname))
    result: ScalarResult
    users = result.all()
    return users