import asyncio
import os
from dataclasses import dataclass
from random import choices, randint, uniform
from typing import Optional
from uuid import UUID

import psycopg2
from aiohttp import ClientSession
from aiohttp.client_exceptions import (ClientPayloadError, ContentTypeError,
                                       ServerDisconnectedError)
from alive_progress import alive_bar
from backoff import expo, on_exception
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from loguru import logger
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from sqlalchemy.orm import Session
from toolz import partition

import event_generator.db as db
from event_generator.models import LoginUsers, User

load_dotenv(find_dotenv())


def generate_users(number_of_users: int = 10) -> tuple[User, ...]:
    faker = Faker()
    return tuple(
        User(
            login=faker.name().replace(" ", "_"),
            password=faker.password(),
            email=faker.email(),
        )
        for _ in range(number_of_users)
    )


def save_users(users: tuple[User, ...]) -> None:
    users_db = db.users

    with Session(db.engine) as session:
        for user in users:
            insert_query = users_db.insert().values(**user.sql_interface)
            session.execute(insert_query)

            session.commit()


def get_users_from_db(number_of_users: Optional[int] = None) -> tuple[User, ...]:
    users_db = db.users

    with Session(db.engine) as session:
        if number_of_users is None:
            return tuple(User(*row[1:-2]) for row in session.query(users_db).all())
        return tuple(
            User(*row[1:-2])
            for row in session.query(users_db).limit(number_of_users).all()
        )


@on_exception(expo, ContentTypeError, max_tries=5)
async def make_several_post_requests(url: str, params: dict) -> dict:
    async with ClientSession(trust_env=True) as session:

        async with session.post(url, json=params) as response:

            if response.status == 409:
                logger.warning("Username or email is already taken!")
            elif response.status == 201:
                logger.info(f'Success signup {params.get("username", "user")}')
            elif response.status == 200:
                name = params.get("username")
                if name is not None:
                    logger.success(f"User {name} was login!")
            return {params["username"]: await response.json()}


async def signup_users(users: tuple[User, ...]) -> dict:
    endpoint = "http://0.0.0.0/auth/v1/signup"

    tasks = []
    for user in users:
        params = user.outer_api_interface
        tasks.append(make_several_post_requests(url=endpoint, params=params))

    return await asyncio.gather(*tasks)


def make_signup(users: tuple[User, ...]):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(signup_users(users))


def signup_users_from_db(number_of_users: int = 10) -> tuple[User, ...]:
    parts = 500

    if number_of_users is None:
        users = get_users_from_db()
    else:
        users = get_users_from_db(number_of_users)

    if number_of_users is not None:
        if number_of_users >= parts:
            users4sign = tuple(partition(parts, users))
            for current_part in users4sign:
                make_signup(current_part)
            return users4sign

    make_signup(users)
    return users


async def login_users(users: tuple[User, ...]) -> dict:
    endpoint = "http://0.0.0.0/auth/v1/login"

    tasks = []
    for user in users:
        params = user.login_info
        tasks.append(make_several_post_requests(url=endpoint, params=params))

    return await asyncio.gather(*tasks)


def make_login(users: tuple[User, ...]) -> dict[str, dict[str, str]]:
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(login_users(users))
    data: dict = {}
    for response in responses:
        data = {**data, **response}
    return data


def update_tokens_in_db(user_login: str, token_1: str, token_2: str) -> None:
    users_db = db.users

    with Session(db.engine) as session:
        session.query(users_db).filter(users_db.c.login == user_login).update(
            {"token_1": token_1, "token_2": token_2}
        )
        session.commit()


def write_tokens_to_db(data: dict[str, dict[str, str]]) -> None:
    for user in data:
        token_1, token_2 = (
            data[user]["access_token"],
            data[user]["refresh_token"],
        )
        update_tokens_in_db(user_login=user, token_1=token_1, token_2=token_2)


def get_users_with_tokens(
    number_of_users: Optional[int] = None,
) -> tuple[LoginUsers, ...]:
    users_db = db.users

    with Session(db.engine) as session:
        condition = users_db.c.token_1.isnot(None) & users_db.c.token_2.isnot(None)
        if number_of_users is None:
            return tuple(
                LoginUsers(*row[1:])
                for row in session.query(users_db).filter(condition).all()
            )
        return tuple(
            LoginUsers(*row[1:])
            for row in session.query(users_db)
            .filter(condition)
            .limit(number_of_users)
            .all()
        )


@on_exception(
    expo, (ContentTypeError, ClientPayloadError, ServerDisconnectedError), max_tries=5
)
async def make_event_request(
    url: str, param_event: dict, auth_token: str, name: Optional[str] = None
) -> dict:

    header = {
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": f"Bearer {auth_token}",
    }
    async with ClientSession() as session:
        async with session.post(url, json=param_event, headers=header) as response:
            if response.status == 200:
                if name is None:
                    name = auth_token[-10:-1]
                # logger.success(
                #     f'Good event '
                #     f'{param_event.keys()} -> {param_event.values()} from {name}'
                # )
            return await response.json()


@dataclass(frozen=True)
class UserEvents:
    __slots__ = ("data", "auth_token", "name")
    data: dict
    auth_token: str
    name: Optional[str]


async def make_users_events(
    data: tuple[dict, ...], auth_token: str, name: Optional[str] = None
) -> list:

    tasks = []
    for info in data:
        endpoint = info.pop("url")
        if name is None:
            event_request = make_event_request(
                url=endpoint, param_event=info, auth_token=auth_token
            )
        else:
            event_request = make_event_request(
                url=endpoint, param_event=info, auth_token=auth_token, name=name
            )
        tasks.append(event_request)

    return await asyncio.gather(*tasks)


def make_events(
    data: tuple[dict, ...], auth_token: str, name: Optional[str] = None
) -> list[dict]:
    loop = asyncio.get_event_loop()
    if name is None:
        return loop.run_until_complete(make_users_events(data, auth_token))
    return loop.run_until_complete(make_users_events(data, auth_token, name))


def get_uuid_films(amount: Optional[int] = 10) -> tuple:
    dsl = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
        "options": "-c search_path=content",
    }
    if amount is None:
        amount = 10
    pg_conn: _connection = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        with pg_conn:
            cursor = pg_conn.cursor()
            cursor.execute(
                "SELECT id FROM content.film_work ORDER BY random() LIMIT %s",
                (amount,),
            )
            result = (str(*_) for _ in cursor.fetchall())
            return tuple(result)
    finally:
        pg_conn.close()


def generate_rating_event(film_id: UUID) -> dict:
    return {
        "url": f"http://0.0.0.0/ugc/api/v1/movies/{film_id}/rating",
        "rating": round(uniform(0, 10), 2),
    }


def generate_view_event(film_id: UUID) -> dict:
    return {
        "url": f"http://0.0.0.0/ugc/api/v1/movies/{film_id}/view",
        "progress": randint(0, 100),
    }


def generate_bookmark_event(film_id: UUID) -> dict:
    return {
        "url": f"http://0.0.0.0/ugc/api/v1/movies/{film_id}/bookmark",
        "bookmarked": bool(randint(0, 1)),
    }


def generate_watched_event(film_id: UUID) -> dict:
    return {
        "url": f"http://0.0.0.0/ugc/api/v1/movies/{film_id}/watched",
        "added": bool(randint(0, 1)),
    }


def generate_random_event(film_id: UUID, number_event: int = 1000) -> tuple[dict, ...]:
    events = (
        generate_rating_event,
        generate_view_event,
        generate_bookmark_event,
        generate_watched_event,
    )
    return tuple(map(lambda el: el(film_id), choices(events, k=number_event)))


def generate_events(
    number_users: int = 1, number_events: int = 10, numbers_films: Optional[int] = 10
):

    users = generate_users(number_users)
    save_users(users)
    users = signup_users_from_db(number_users)
    users_tokens = make_login(users)
    write_tokens_to_db(users_tokens)
    auth_users = get_users_with_tokens(number_users)

    id_films = get_uuid_films(numbers_films)

    logger.success(
        f"{len(auth_users) * len(id_films) * number_events} events will be processed!"
    )
    with alive_bar(
        len(auth_users) * len(id_films), force_tty=True, bar="checks"
    ) as bar:
        for user in auth_users:
            auth_token = user.token_1
            name = user.login
            for film_id in id_films:
                events = generate_random_event(
                    film_id=film_id, number_event=number_events
                )

                make_events(data=events, auth_token=auth_token, name=name)
                # logger.info(f"{len(events)} events have been added")
                bar()

    logger.success(
        f"{len(auth_users) * len(id_films) * number_events} events have been added!"
    )
