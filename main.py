import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base
from middlewares import DbSessionMiddleware
from config import db_url, TOKEN
from forms import form_router
from qiuz import quiz_router
from handlers.handler_app import any_router
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()


async def main():
    engine = create_async_engine(db_url, echo=True)
    session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
     
    bot = Bot(TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(form_router)
    dp.include_router(quiz_router)
    dp.include_router(any_router)
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
        

    await dp.start_polling(bot, session_maker=session_maker)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')