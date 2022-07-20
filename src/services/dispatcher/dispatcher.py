import asyncio

from services.fetcher.fetcher import \
    fetch_cards, \
    fetch_model_images, \
    download_images, \
    is_valid_page
from services.database.services import *
from services.extern.image_validator import purge_invalid_images


async def load_data_for_card(card):
    db_card = await get_card_by_link(card.link)
    if db_card is None:
        print("Creating card: ", card.title, " link: ", card.link)
        try:
            images = await fetch_model_images(card)
            filenames = await download_images(card, images)
        except Exception as e:
            print(f"Cannot fetch model's images: {card.title}, '{e}'")
            return None
        return await create_card(
            model_name=card.title,
            image_paths=filenames,
            real_link=card.link,
            preview_image=card.preview_image,
            views_count=card.views_count,
            photos_count=card.photos_count
        )
    else:
        print(f"Card: {card.title} was already loaded")


async def full_reload_database():
    page = 1
    while is_valid_page(page):
        cards = await fetch_cards(page)

        load_data_for_card_tasks = [asyncio.create_task(load_data_for_card(card)) for card in cards]
        await asyncio.gather(*load_data_for_card_tasks)
        page += 1

    # Loading the images, some of them are in an unknown format and cannot be read by PIL.Image
    # or Telegram, so I need to purge them
    await purge_invalid_images()


