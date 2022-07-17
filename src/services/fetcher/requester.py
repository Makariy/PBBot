import aiohttp
from bs4 import BeautifulSoup as Soup


async def download_image(url: str) -> bytes:
    session = aiohttp.ClientSession()
    async with session.get(url) as response:
        return await response.content.read()


async def request(url: str) -> Soup:
    session = aiohttp.ClientSession()
    async with session.get(url) as response:
        return Soup(await response.text(), 'html.parser')

