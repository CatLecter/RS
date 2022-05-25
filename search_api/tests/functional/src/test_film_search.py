import math
from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_films_search(
    create_index,
    make_get_request,
    test_data,
):
    film_test_data = await test_data("movies")
    expected_items = [
        {
            "uuid": _["uuid"],
            "title": _["title"],
            "imdb_rating": float(_["imdb_rating"]),
        }
        for _ in film_test_data
    ]
    for i in range(len(expected_items)):
        tested_film = expected_items[i]
        response = await make_get_request(
            "/films/search/", params={"query": tested_film["title"]}
        )
        assert response.status == HTTPStatus.OK
        assert response.body["items"][0] == tested_film


@pytest.mark.asyncio
async def test_films_search_not_found(create_index, make_get_request):
    response = await make_get_request("/films/search/", params={"query": "NotFound"})
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == []
    assert response.body["total"] == 0
    assert response.body["page_size"] == 20
    assert response.body["page_number"] == 1


@pytest.mark.asyncio
async def test_films_pagination(
    create_index,
    make_get_request,
    test_data,
):
    films_test_data = await test_data("movies")
    page_size = 2
    pages = math.ceil(len(films_test_data) / page_size)
    for page in range(1, pages):
        response = await make_get_request(
            "/films/search/", params={"page[number]": page, "page[size]": page_size}
        )
        assert response.status == HTTPStatus.OK
        assert response.body["total"] == 10
        assert response.body["page_size"] == page_size
        assert response.body["page_number"] == page


@pytest.mark.asyncio
async def test_films_all(create_index, make_get_request, test_data):
    films_test_data = await test_data("movies")
    expected_items = [
        {
            "uuid": _["uuid"],
            "title": _["title"],
            "imdb_rating": _["imdb_rating"],
        }
        for _ in films_test_data
    ]
    response = await make_get_request(
        "/films/search/", params={"page[number]": 1, "page[size]": 10}
    )
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == expected_items
    assert response.body["total"] == 10
    assert response.body["page_size"] == 10
    assert response.body["page_number"] == 1
