from dataclasses import dataclass


@dataclass
class CardPreview:
    title: str
    link: str
    preview_image: str
    views_count: int
    photos_count: int

