import abc
import json
from pathlib import Path
from typing import Any, Dict

from log_utils import get_logger

storage_path = Path("state_storage.json")
logger = get_logger(__name__)


class BaseStorage:
    """
    Абстрактный класс хранилища для сохранения состояния.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict) -> None:
        """Сохраняет состояние в постоянное хранилище."""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> Dict:
        """Загружает состояние из постоянного хранилища."""
        pass


class JsonFileStorage(BaseStorage):
    """
    Реализация хранилища использующая файлы для сохранения состояния.
    """

    def __init__(self, file_path: Path = None):
        self.file_path = file_path

    def save_state(self, state: Dict) -> None:
        """Сохраняет состояние в постоянное хранилище."""
        with self.file_path.open(mode="w+", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False)

    def retrieve_state(self) -> Dict:
        """Загружает состояние из постоянного хранилища."""
        if not self.file_path.is_file():
            logger.warning(
                f'Не могу получить состояние! Файл "{self.file_path}" не существует!'
            )
            return {}
        try:
            with self.file_path.open(mode="r", encoding="utf-8") as f:
                file_content = f.read().strip()
                if not file_content:
                    return {}
                return json.loads(file_content)
        except json.JSONDecodeError as e:
            logger.warning(f'Ошибка чтения состояния из файла "{self.file_path}": {e}')
            return {}


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Устанавливает состояние для определённого ключа."""
        data = self.storage.retrieve_state()
        data[key] = value
        logger.debug(f'Устанавливаем значение "{value}" для ключа "{key}".')
        self.storage.save_state(data)

    def get_state(self, key: str, default: Any = None) -> Any:
        """Возвращает состояние по определённому ключу."""
        data = self.storage.retrieve_state()
        if key not in data:
            logger.warning(f'Ключ "{key}" не найден! Возвращено значение "{default}".')
            return default
        value = data[key]
        logger.debug(f'Возвращено значение "{value}" для ключа "{key}".')
        return value


def get_state() -> State:
    """Возвращает состояние работы с данными."""
    if not storage_path.is_file():
        storage_path.touch(exist_ok=True)

    state_storage = JsonFileStorage(storage_path)
    state_instance = State(state_storage)
    return state_instance
