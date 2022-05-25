from models.film import FilmFilterType, FilmSortingType

DEFAULT_PAGE_NUMBER = {
    "alias": "page[number]",
    "title": "Страница",
    "default": 1,
    "ge": 1,
    "description": "Номер страницы.",
}

DEFAULT_PAGE_SIZE = {
    "alias": "page[size]",
    "title": "Размер",
    "default": 20,
    "ge": 1,
    "le": 100,
    "description": "Результатов на странице.",
}

DEFAULT_UUID = {
    "title": "UUID объекта",
    "default": None,
    "description": "Поиск объекта по его UUID.",
    "example": "2f89e116-4827-4ff4-853c-b6e058f71e31",
}

DEFAULT_QUERY = {
    "title": "Поиск",
    "default": None,
    "description": "Поиск по тексту.",
    "example": "Captain",
}

DEFAULT_FILM_SORT = {
    "title": "Сортировка",
    "default": None,
    "description": "Критерий сортировки.",
    "example": FilmSortingType.imdb_rating_desc,
}

DEFAULT_FILM_FILTER_TYPE = {
    "default": None,
    "title": "Тип фильтрации",
    "description": "Выберите тип фильтрации из предложенных.",
    "example": FilmFilterType.genre,
}

DEFAULT_FILM_FILTER_VALUE = {
    "default": None,
    "title": "Значение для фильтрации",
    "description": "UUID для сортировки по выбранному типу.",
    "example": "0b105f87-e0a5-45dc-8ce7-f8632088f390",
}
