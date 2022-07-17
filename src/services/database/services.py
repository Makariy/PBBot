from typing import List, Union
from services.database.models import *
from tortoise.exceptions import DoesNotExist
from .exceptions import NotUniqueException


async def get_images_by_model(model: OFModel) -> List[Image]:
    card = await Card.get(model=model).prefetch_related('images')
    return card.images


async def get_card_by_link(link: str) -> Union[Card, None]:
    try:
        return await Card.get(real_link=link)
    except DoesNotExist:
        return None


async def get_ofmodel_by_name(name: str) -> Union[OFModel, None]:
    try:
        return await OFModel.get(name=name)
    except DoesNotExist:
        return None


async def get_all_ofmodels(name: str = "") -> List[OFModel]:
    result = OFModel.all()
    if name:
        result = result.filter(name__startswith=name)
    return await result


async def get_image_by_path(path: str) -> Union[Image, None]:
    try:
        return await Image.get(file=path)
    except DoesNotExist:
        return None


async def create_model(name: str) -> OFModel:
    if await get_ofmodel_by_name(name) is not None:
        raise NotUniqueException(f"Model: '{name}' was already created")
    return await OFModel.create(name=name)


async def create_image(path: str) -> Image:
    if await get_image_by_path(path) is not None:
        raise NotUniqueException(f"Image: '{path}' was already saved")
    return await Image.create(file=path)


async def create_card(model_name: str,
                      image_paths: List[str],
                      real_link: str,
                      preview_image: str,
                      views_count: int,
                      photos_count: int) -> Card:
    model = await get_ofmodel_by_name(model_name)
    if model is None:
        model = await create_model(model_name)
    images = []
    for path in image_paths:
        images.append(await create_image(path))
    card = await Card.create(
        model=model,
        real_link=real_link,
        preview_image=preview_image,
        views_count=views_count,
        photos_count=photos_count
    )
    await card.images.add(*images)
    return card


