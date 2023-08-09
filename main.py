import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Base
from middlewares import DbSessionMiddleware
from config import db_url, TOKEN
from handlers.register import form_router
from handlers.qiuz import quiz_router
from handlers.handler_app import any_router
from utils.scheduler import quiz_scheduler


async def main():
    engine = create_async_engine(db_url, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
     
    bot = Bot(TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(form_router)
    dp.include_router(quiz_router)
    dp.include_router(any_router)
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(quiz_scheduler, 'cron', second=30, args=(bot, dp.storage, async_session))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    scheduler.start()

    await dp.start_polling(bot, engine=engine)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')