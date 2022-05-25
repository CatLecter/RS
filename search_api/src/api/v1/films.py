from http import HTTPStatus
from typing import Optional

from core import endpoints_params as ep_params
from core.config import NOT_FOUND_MESSAGE
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from models.film import Film, FilmBrief, FilmFilterType, FilmSortingType
from models.general import Page
from services.film import FilmService
from services.getters import get_film_service

router = APIRouter(prefix="/films", tags=["Фильмы"])


@router.get(
    path="/{uuid}",
    name="Детали фильма",
    description="Получение детальной информации по фильму.",
    response_model=Film,
)
async def film_details(
    uuid: str = Query(**ep_params.DEFAULT_UUID),
    film_service: FilmService = Depends(get_film_service),
) -> Film:
    result = await film_service.get_by_uuid(uuid)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=NOT_FOUND_MESSAGE)
    return result


@router.get(
    path="/search/",
    name="Поиск фильмов",
    description="Поиск фильмов по заголовку или описанию.",
    response_model=Page[FilmBrief],
)
async def film_search(
    query: str = Query(**ep_params.DEFAULT_QUERY),
    page_number: Optional[int] = Query(**ep_params.DEFAULT_PAGE_NUMBER),
    page_size: Optional[int] = Query(**ep_params.DEFAULT_PAGE_SIZE),
    film_service: FilmService = Depends(get_film_service),
) -> Page[FilmBrief]:
    page = await film_service.search(query, page_number, page_size)
    return page


@router.get(
    path="/",
    name="Сортировка и фильтрация фильмов",
    description="Список фильмов по заданным критериям сортировки и фильтрации.",
    response_model=Page[FilmBrief],
)
async def film_list(
    request: Request,
    sort: Optional[FilmSortingType] = Query(**ep_params.DEFAULT_FILM_SORT),
    filter_type: Optional[FilmFilterType] = Query(**ep_params.DEFAULT_FILM_FILTER_TYPE),
    filter_value: Optional[str] = Query(**ep_params.DEFAULT_FILM_FILTER_VALUE),
    page_number: Optional[int] = Query(**ep_params.DEFAULT_PAGE_NUMBER),
    page_size: Optional[int] = Query(**ep_params.DEFAULT_PAGE_SIZE),
    film_service: FilmService = Depends(get_film_service),
) -> Page[FilmBrief]:
    allowed_roles = {"subscriber", "contributor", "editor", "administrator"}
    if not allowed_roles.intersection(request.state.user_roles):
        # Анонимным пользователям разрешаем просматривать только первую страницу.
        page_number = 1
        page_size = 20
    page = await film_service.get_sorted_filtered(
        sort, filter_type, filter_value, page_number, page_size
    )
    return page
