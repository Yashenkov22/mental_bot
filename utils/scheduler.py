import asyncio
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries import get_all_user_ids
from handlers.qiuz import start_quiz


async def quiz_scheduler(bot: Bot, storage, session: AsyncSession):
    user_ids = await get_all_user_ids(session)
    # print(user_ids)
    tasks = []
    for user_id in user_ids:
        user_id = user_id[0]
        state = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id,
                           chat_id=user_id,
                           user_id=user_id)
        )
        tasks.append(asyncio.create_task(start_quiz(bot=bot, user_id=user_id, state=state)))

    await asyncio.gather(*tasks)