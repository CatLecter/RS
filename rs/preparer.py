from http import HTTPStatus

import aiohttp
import backoff
from aiohttp import ClientConnectionError, ClientError
from config import TABLES
from models import BookmarkEvent, Movie, MovieBrief, RatingEvent, ViewEvent, WatchEvent
from orjson import loads


@backoff.on_exception(backoff.expo, ClientConnectionError, max_tries=3)
async def get_movie(movie_uuid: str):
    url = f"http://10.5.0.1/api/v1/films/{movie_uuid}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == HTTPStatus.OK:
                    _movie = await resp.text()
                    movie = Movie(**loads(_movie))
                    genres = [genre["name"] for genre in movie.dict()["genres"]]
                    return MovieBrief(
                        uuid=movie.uuid,
                        genres=genres,
                    )
                else:
                    return MovieBrief(
                        uuid=movie_uuid,
                    )
    except ClientError:
        return MovieBrief(uuid=movie_uuid)


async def processing(data: dict) -> tuple[list, list, list, list]:
    bookmarks: list = []
    ratings: list = []
    views: list = []
    watched: list = []
    for table in TABLES:
        if table == "bookmarks":
            for event in data[table]:
                movie = await get_movie(movie_uuid=event[1])
                bookmark = BookmarkEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    bookmarked=event[3],
                )
                bookmarks.append(bookmark.dict())
        elif table == "ratings":
            for event in data[table]:
                movie = await get_movie(movie_uuid=event[1])
                rating = RatingEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    rating=event[3],
                )
                ratings.append(rating.dict())
        elif table == "views":
            for event in data[table]:
                movie = await get_movie(movie_uuid=event[1])
                view = ViewEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    progress=event[3],
                )
                views.append(view.dict())
        elif table == "watched":
            for event in data[table]:
                movie = await get_movie(movie_uuid=event[1])
                watch = WatchEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    added=event[3],
                )
                watched.append(watch.dict())
    return bookmarks, ratings, views, watched
