from json import loads
from uuid import UUID

import backoff
from http import HTTPStatus
from db.elastic import ElasticSearchEngine, get_es_search
from fastapi import APIRouter, HTTPException
from models.rs_models import (Movie)
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError

router = APIRouter(prefix="/rs_movies", tags=["Рекомендованые Фильмы"])


@backoff.on_exception(backoff.expo, HTTPError, max_tries=3)
def get_movie(movie_uuid: str):
    try:
        http = PoolManager()
        movie = http.request("GET", f"http://10.5.0.1/api/v1/films/{movie_uuid}")

        if movie.status == 200:
            movie = Movie(**loads(movie.data.decode("UTF-8")))
            return movie

    except HTTPError:
        pass


@router.get(
    path="/{person_uuid}",
    name="Рекомендация для пользователя.",
    description="Получение детальной информации рекомендованых фильмов.",
    response_model=list[Movie]
)
async def genre_details(
    person_uuid: UUID,
):
    es_ser = ElasticSearchEngine(get_es_search())

    films = await es_ser.get_by_pk(table="movies", pk=person_uuid)

    if films is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Пользователь не найден."
        )

    movies = []
    for film_id in films["movies"]:
        film_info = get_movie(film_id)
        if film_info is None:
            continue

        movies.append(film_info)
    return movies
