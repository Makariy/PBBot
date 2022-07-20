import os

from .path_maker import get_path_for_item


def save_data_to_file(root: str, filename: str, content: bytes) -> str:
    path = get_path_for_item(root)
    if not os.path.exists(path):
        os.mkdir(path)

    with open(os.path.join(path, filename), 'wb') as file:
        file.write(content)
    return os.path.join(root, filename)


