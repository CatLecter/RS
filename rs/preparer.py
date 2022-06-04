from json import loads

import backoff
from config import TABLES, log_config
from loguru import logger
from models import (
    BookmarkEvent,
    LanguageEvent,
    Movie,
    MovieBrief,
    RatingEvent,
    ViewEvent,
    WatchEvent,
)
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError

logger.add(**log_config)


@backoff.on_exception(backoff.expo, HTTPError, max_tries=3)
def get_movie(movie_uuid: str):
    try:
        http = PoolManager()
        movie = http.request("GET", f"http://10.5.0.1/api/v1/films/{movie_uuid}")
        if movie.status == 200:
            movie = Movie(**loads(movie.data.decode("UTF-8")))
            genres = [genre["name"] for genre in movie.dict()["genres"]]
            return MovieBrief(
                uuid=movie.uuid,
                genres=genres,
            )
        else:
            return MovieBrief(
                uuid=movie_uuid,
            )
    except HTTPError:
        return MovieBrief(uuid=movie_uuid)


def processing(data: dict) -> tuple:
    bookmarks: list = []
    languages: list = []
    ratings: list = []
    views: list = []
    watched: list = []
    for table in TABLES:
        if table == "bookmarks":
            for event in data[table]:
                movie = get_movie(movie_uuid=event[1])
                bookmark = BookmarkEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    bookmarked=event[3],
                )
                bookmarks.append(bookmark.dict())
        elif table == "language":
            for event in data[table]:
                movie = get_movie(movie_uuid=event[1])
                language = LanguageEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    language_movie=event[3],
                    language_client=event[4],
                )
                languages.append(language.dict())
        elif table == "ratings":
            for event in data[table]:
                movie = get_movie(movie_uuid=event[1])
                rating = RatingEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    rating=event[3],
                )
                ratings.append(rating.dict())
        elif table == "views":
            for event in data[table]:
                movie = get_movie(movie_uuid=event[1])
                view = ViewEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    progress=event[3],
                )
                views.append(view.dict())
        elif table == "watched":
            for event in data[table]:
                movie = get_movie(movie_uuid=event[1])
                watch = WatchEvent(
                    user_uuid=event[0],
                    movie=movie,
                    datetime=event[2],
                    added=event[3],
                )
                watched.append(watch.dict())
    return bookmarks, languages, ratings, views, watched