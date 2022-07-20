import os
import config


def get_path_for_item(file_path: str) -> str:
    return os.path.join(config.SAVING_ROOT, file_path)
