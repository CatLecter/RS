import asyncio
import nest_asyncio
from json import loads
from uuid import UUID
from typing import Literal

import backoff
from aiohttp import ClientSession, TCPConnector, ClientConnectionError
from http import HTTPStatus
from db.elastic import ElasticSearchEngine, get_es_search
from fastapi import APIRouter, HTTPException
from models.rs_models import (Movie)
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError

router = APIRouter(prefix="/rs_movies", tags=["Рекомендованые Фильмы"])
nest_asyncio.apply()


async def get_movies(movie_uuid: UUID) -> Movie | None:
    url = f"http://10.5.0.1/api/v1/films/{movie_uuid}"
    try:
        async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
            async with session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    return {movie_uuid: Movie(**await response.json())}
    except ClientConnectionError:
        return {movie_uuid: None}


async def get_rec_movies(user_uuid: UUID) -> dict[UUID, list[UUID]]:
    return {
        user_uuid: await (ElasticSearchEngine(get_es_search())
                          .get_by_pk(table="movies", pk=user_uuid))
    }


async def get_request(uuid: list[UUID], type_: Literal["movies", "rs_films"]):
    if type_ == "movies":
        tasks = (get_movies(current_uuid) for current_uuid in uuid)
    else:
        tasks = (get_rec_movies(current_uuid) for current_uuid in uuid)

    return await asyncio.gather(*tasks)


def make_requests_by_uuid(
    uuid: list[UUID],
    type_: Literal["movies", "rs_films"]
) -> list:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(get_request(uuid=uuid, type_=type_))


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
async def rs_movie4user(
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


@router.post(
    path="/recommendation_movies",
    name="Рекомендации для пользователей.",
    description="Получение детальной информации рекомендованых фильмов пользователей.",
    # response_model=dict[str, list[Movie]]
)
def rs_movie4users(
    persons_uuid: list[UUID]
):
    persons_with_films = make_requests_by_uuid(uuid=persons_uuid, type_="rs_films")

    persons_and_films = {}
    for el in persons_with_films:
        persons_and_films = persons_and_films | el

    persons_and_films = {
        user_uuid:
            persons_and_films[user_uuid]['movies'] for user_uuid in persons_and_films
    }

    movies_id = []
    for user_id in persons_and_films:
        movies_id += persons_and_films[user_id]

    movies_full_info = make_requests_by_uuid(uuid=movies_id, type_="movies")
    full_films = {}
    for el in movies_full_info:
        full_films = full_films | el

    out_response = {}
    for user_id in persons_and_films:
        out_response[user_id] = {}
        for film_id in persons_and_films[user_id]:
            out_response[user_id][film_id] = full_films[film_id]

    return out_response
