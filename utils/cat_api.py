import aiohttp
import asyncio

async def get_cat(tag: str, words: str):
    async with aiohttp.ClientSession() as session:
            async with session.get(f'https://cataas.com/cat/{tag}/says/{words}') as response:
                return await response.content.read()
            
# asyncio.run(get_cat('what up'))