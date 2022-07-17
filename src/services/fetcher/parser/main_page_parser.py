from typing import List, Union
from bs4 import BeautifulSoup as Soup

from services.fetcher.models import CardPreview
from services.fetcher.requester import request
from .paginator import make_url
from .. import logger


class MainPageParser:
    @staticmethod
    def _parse_card_title( card: Soup) -> str:
        return card.find(**{'class': 'item-title'}).text

    @staticmethod
    def _parse_card_link(card: Soup) -> str:
        return card.find(**{'class': 'item-link'}).get_attribute_list('href')[0]

    @staticmethod
    def _parse_card_preview_image(card: Soup) -> str:
        return card.find(**{'class': 'item-img'}).find('img').get_attribute_list('src')[0]

    @staticmethod
    def _parse_card_views_count(card: Soup) -> int:
        try:
            return int(card.find(**{'class': 'meta-views'}).text.replace(' ', ''))
        except ValueError:
            logger.warning(f"Cannot parse card's 'views_count' for card: {MainPageParser._parse_card_link(card)}")
            return -1

    @staticmethod
    def _parse_card_photos_count(card: Soup) -> int:
        try:
            return int(card.find(**{'class': 'meta-time'}).text.replace(' ', ''))
        except ValueError:
            logger.warning(f"Cannot parse card's 'photos_count' for card: {MainPageParser._parse_card_link(card)}")
            return -1

    @staticmethod
    def _parse_card(card: Soup) -> Union[CardPreview, None]:
        try:
            return CardPreview(
                title=MainPageParser._parse_card_title(card),
                link=MainPageParser._parse_card_link(card),
                preview_image=MainPageParser._parse_card_preview_image(card),
                views_count=MainPageParser._parse_card_views_count(card),
                photos_count=MainPageParser._parse_card_photos_count(card)
            )
        except (ValueError, TypeError, IndexError) as e:
            logger.warning(f"Cannot parse card '{MainPageParser._parse_card_title(card)}', exception: '{e}'")

    @staticmethod
    def _parse_cards(cards: List[Soup]) -> List[CardPreview]:
        return list(filter(lambda a: a is not None, [MainPageParser._parse_card(card) for card in cards]))

    @staticmethod
    def _get_raw_cards(page: Soup) -> List[Soup]:
        return page.find_all(**{'class': 'item'})

    @staticmethod
    async def get_all_cards(url: str, page: int) -> List[CardPreview]:
        page = await request(make_url(url, page))
        raw_cards = MainPageParser._get_raw_cards(page)
        return MainPageParser._parse_cards(raw_cards)
