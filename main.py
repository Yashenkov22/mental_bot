import asyncio

from uvicorn import Config, Server

from fastapi import FastAPI

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.models import Base
from middlewares import DbSessionMiddleware
from config import db_url, TOKEN, NGROK_PUBLIC_URL
from handlers.register import register_router
from handlers.qiuz import quiz_router
from handlers.admin import admin_router
from handlers.manage_subscribe import subscribe_router
from handlers.user import user_router
from handlers.pictures import pictures_router
from handlers.excel import excel_router
from utils.scheduler import quiz_scheduler


#For set webhook
WEBHOOK_PATH = f'/{TOKEN}'

#Database connection
engine = create_async_engine(db_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

#Create database
async def start_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

#Initialize bot
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

#Add routers to dispatcher
dp.include_router(register_router)
dp.include_router(quiz_router)
dp.include_router(admin_router)
dp.include_router(subscribe_router)
dp.include_router(user_router)
dp.include_router(pictures_router)
dp.include_router(excel_router)

#Add session and database connection in handlers 
dp.update.middleware(DbSessionMiddleware(session_pool=async_session,
                                         engine=engine))

#Initialize web server
app = FastAPI()
event_loop = asyncio.get_event_loop()
config = Config(app=app,
                loop=event_loop,
                host='0.0.0.0',
                port=8000)
server = Server(config)

#Set webhook and create database on start
@app.on_event('startup')
async def on_startup():
    await bot.set_webhook(f"{NGROK_PUBLIC_URL}{WEBHOOK_PATH}",
                          drop_pending_updates=True)
    await start_db()

#Endpoint for checking
@app.get(WEBHOOK_PATH)
async def any():
    return {'status': 'ok'}

#Endpoint for incoming updates
@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    tg_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=tg_update)


#Initialize AsyncScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(quiz_scheduler, 'cron', second=30, args=(bot, dp.storage, async_session))
scheduler.start()


if __name__ == '__main__':
    event_loop.run_until_complete(server.serve())
