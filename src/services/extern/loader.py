import os
import config


def load_file_data(path: str) -> bytes:
    with open(os.path.join(config.SAVING_ROOT, path), 'rb') as file:
        return file.read()

