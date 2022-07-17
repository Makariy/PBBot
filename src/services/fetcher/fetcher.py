import os
import shutil
import asyncio
from typing import List
from services.fetcher.models import CardPreview

from .parser.main_page_parser import MainPageParser
from .parser.model_page_parser import ModelPageParser
from . import logger

from .requester import download_image
from services.extern.saver import save_data_to_file, delete_directory
from uuid import uuid4

import config


async def _download_image(root: str, src: str) -> str:
    content = await download_image(src)
    filename = str(uuid4())
    return save_data_to_file(root, filename, content)


async def download_images(card: CardPreview, srcs: List[str]) -> List[str]:
    try:
        get_filenames_tasks = [asyncio.create_task(_download_image(card.title, src)) for src in srcs]
        filenames = await asyncio.gather(*get_filenames_tasks)
        return [f"{card.title}/{filename}" for filename in filenames]

    except Exception as e:
        delete_directory(card.titel)
        raise e


async def fetch_model_images(card: CardPreview) -> List[str]:
    return await ModelPageParser.parse_all_photos(card.link)


async def fetch_cards(page: int) -> List[CardPreview]:
    logger.info("Fetching cards")
    return await MainPageParser.get_all_cards(config.FETCHING_URL, page)


def is_valid_page(page: int) -> bool:
    if 0 < page <= 18:
        return True
    return False

