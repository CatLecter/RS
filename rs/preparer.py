from json import loads

import backoff
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError

from config import TABLES
from models import BookmarkEvent, Movie, MovieBrief, RatingEvent, ViewEvent, WatchEvent


@backoff.on_exception(backoff.expo, HTTPError, max_tries=3)
def get_movie(movie_uuid: str):
    try:
        http = PoolManager()
        movie = http.request("GET", f"http://0.0.0.0/api/v1/films/{movie_uuid}")
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
    return bookmarks, ratings, views, watched
