from typing import List, Union
from bs4 import BeautifulSoup as Soup

from services.fetcher.requester import request
from .. import logger


class ModelPageParser:
    @staticmethod
    def _parse_photo_link(photo: Soup) -> Union[str, None]:
        try:
            return photo.get_attribute_list('src')[0]
        except IndexError:
            logger.warning(f"Cannot parse photo's src, photo: '{photo}'")
            return None

    @staticmethod
    def _parse_photos(photos: Soup) -> List[str]:
        return list(filter(lambda a: a is not None,
                           [ModelPageParser._parse_photo_link(photo)
                            for photo in photos.find_all(**{'class': 'fr-fic'})]
                           ))

    @staticmethod
    async def parse_all_photos(url: str) -> List[str]:
        page = await request(url)
        photos_div = page.find(**{'class': 'f-desc'})
        return ModelPageParser._parse_photos(photos_div)

