import os
import shutil

import config


def save_data_to_file(root: str, filename: str, content: bytes) -> str:
    path = os.path.join(config.SAVING_ROOT, root)
    if not os.path.exists(path):
        os.mkdir(path)

    with open(os.path.join(path, filename), 'wb') as file:
        file.write(content)
    return os.path.join(root, filename)


def delete_directory(directory: str):
    shutil.rmtree(os.path.join(config.SAVING_ROOT, directory))
