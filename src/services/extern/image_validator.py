from typing import List
from PIL import UnidentifiedImageError, Image as PImage

from .path_maker import get_path_for_item
from services.database.models import Image
from services.database.services import get_all_images, delete_image


async def is_image_valid(image: Image) -> bool:
    try:
        PImage.open(get_path_for_item(image.file))
        return True
    except UnidentifiedImageError:
        return False


async def get_not_valid_images(images: List[Image]) -> List[Image]:
    invalid_images = []
    for image in images:
        if not await is_image_valid(image):
            invalid_images.append(image)
    return invalid_images


async def purge_invalid_images():
    images = await get_all_images()
    invalid_images = await get_not_valid_images(images)
    for image in invalid_images:
        await delete_image(image)

