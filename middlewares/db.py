from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self,
                 session_pool: async_sessionmaker,
                 engine: AsyncEngine):
        super().__init__()
        self.session_pool = session_pool
        self.engine = engine

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        
        data['engine'] = self.engine

        async with self.session_pool() as session:
            data["session"] = session
        
            return await handler(event, data)
