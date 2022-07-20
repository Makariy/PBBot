import os
import shutil
from .path_maker import get_path_for_item


def delete_file(file_path: str):
    path = get_path_for_item(file_path)
    if not os.path.exists(path):
        raise FileNotFoundError
    os.remove(path)


def delete_directory(directory: str):
    path = get_path_for_item(directory)
    if not os.path.exists(path):
        raise NotADirectoryError
    shutil.rmtree(path)
