import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from aiohttp import web

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Base
from middlewares import DbSessionMiddleware
from config import db_url, TOKEN
from handlers.register import register_router
from handlers.qiuz import quiz_router
from handlers.admin import admin_router
from handlers.excel import excel_router
from utils.scheduler import quiz_scheduler

#For set webhook
WEB_SERVER_HOST = '127.0.0.1'
WEB_SERVER_PORT = 8080

WEBHOOK_PATH = f'/{TOKEN}'
BASE_WEBHOOK_URL = 'https://ffc6-178-217-121-185.ngrok.io'

#Database connection
engine = create_async_engine(db_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

#Initialize bot
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

#Add routers to dispatcher
dp.include_router(register_router)
dp.include_router(quiz_router)
dp.include_router(admin_router)
dp.include_router(excel_router)

#Add session and database connection in handlers 
dp.update.middleware(DbSessionMiddleware(session_pool=async_session,
                                         engine=engine))

#Set webhook on start
async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
                          drop_pending_updates=True)

dp.startup.register(on_startup)

#Initialize web server
app = web.Application()

#Webhook hendler
webhook_requests_handler = SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
)

#Bind webhook with webserver
webhook_requests_handler.register(app, path=WEBHOOK_PATH)

setup_application(app, dp, bot=bot)

#Initialize AsyncScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(quiz_scheduler, 'cron', second=30, args=(bot, dp.storage, async_session))
scheduler.start()


#Create database with start webserver
async def start_db(app):
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

app.on_startup.append(start_db)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    web.run_app(app,
                host=WEB_SERVER_HOST,
                port=WEB_SERVER_PORT,
                loop=event_loop)