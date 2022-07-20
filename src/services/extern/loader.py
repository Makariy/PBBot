from .path_maker import get_path_for_item


def load_file_data(path: str) -> bytes:
    with open(get_path_for_item(path), 'rb') as file:
        return file.read()

