import os
from pathlib import Path
from typing import Union


def names_file(path: Union[str, Path]):
    """Возвращает лист с названием файлов в папке."""

    files = os.walk(str(path))
    list_idx = []
    for idx in files:
        list_idx = idx[2]
    return [_.split(".")[0] for _ in list_idx]
