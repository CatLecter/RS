import asyncio
from http import HTTPStatus
from typing import Literal
from uuid import UUID

import aiohttp
import backoff
import nest_asyncio
from aiohttp import ClientConnectionError, ClientError
from db.elastic import ElasticSearchEngine, get_es_search
from fastapi import APIRouter, HTTPException
from models.rs_models import Movie
from orjson import loads

router = APIRouter(prefix="/rs_movies", tags=["Рекомендованые Фильмы"])
nest_asyncio.apply()


@backoff.on_exception(backoff.expo, ClientConnectionError, max_tries=3)
async def get_movies(movie_uuid: UUID) -> Movie | None:
    url = f"http://10.5.0.1/api/v1/films/{movie_uuid}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == HTTPStatus.OK:
                    movie = await resp.text()
                    return {movie_uuid: Movie(**loads(movie))}
    except ClientError:
        return {movie_uuid: None}


async def get_rec_movies(user_uuid: UUID) -> dict[UUID, list[UUID]]:
    return {
        user_uuid: await (
            ElasticSearchEngine(get_es_search()).get_by_pk(table="movies", pk=user_uuid)
        )
    }


async def get_request(uuid: list[UUID], type_: Literal["movies", "rs_films"]):
    if type_ == "movies":
        tasks = (get_movies(current_uuid) for current_uuid in uuid)
    else:
        tasks = (get_rec_movies(current_uuid) for current_uuid in uuid)

    return await asyncio.gather(*tasks)


def make_requests_by_uuid(
    uuid: list[UUID], type_: Literal["movies", "rs_films"]
) -> list:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(get_request(uuid=uuid, type_=type_))


@backoff.on_exception(backoff.expo, ClientConnectionError, max_tries=3)
async def get_movie(movie_uuid: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://10.5.0.1/api/v1/films/{movie_uuid}") as resp:
            if resp.status == HTTPStatus.OK:
                movie = await resp.text()
                return Movie(**loads(movie))


@router.get(
    path="/{user_uuid}",
    name="Рекомендация для пользователя.",
    description="Получение детальной информации о фильмах рекомендованных "
    "пользователю к просмотру по его UUID.",
    response_model=list[Movie],
)
async def rs_movie4user(
    user_uuid: UUID,
):
    es_ser = ElasticSearchEngine(get_es_search())

    films = await es_ser.get_by_pk(table="movies", pk=user_uuid)

    if films is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Пользователь не найден."
        )

    movies = []
    for film_id in films["movies"]:
        film_info = await get_movie(film_id)
        if film_info is None:
            continue

        movies.append(film_info)
    return movies


@router.post(
    path="/users_list",
    name="Рекомендации для списка пользователей.",
    description="Получение детальной информации о рекомендациях для "
    "нескольких пользвателей по списку их UUID.",
)
def rs_movie4users(persons_uuid: list[UUID]):
    persons_with_films = make_requests_by_uuid(uuid=persons_uuid, type_="rs_films")

    persons_and_films = {}
    for el in persons_with_films:
        persons_and_films = persons_and_films | el

    persons_and_films = {
        user_uuid: persons_and_films[user_uuid]["movies"]
        for user_uuid in persons_and_films
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
