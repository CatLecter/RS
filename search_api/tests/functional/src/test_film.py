from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_film(create_index, make_get_request, test_data):
    expected_result = await test_data("movies")
    for i in range(len(expected_result)):
        tested_film = expected_result[i]
        response = await make_get_request(f"/films/{tested_film['uuid']}", params={})
        print("\n")
        sorted_response = dict(sorted(response.body.items(), key=lambda x: x[0]))
        sorted_film = dict(sorted(tested_film.items(), key=lambda x: x[0]))
        sorted_film.pop("actors_names")
        sorted_film.pop("directors_names")
        sorted_film.pop("writers_names")
        sorted_film["imdb_rating"] = float(sorted_film["imdb_rating"])
        assert response.status == HTTPStatus.OK
        assert sorted_response == sorted_film


@pytest.mark.asyncio
async def test_film_not_found(create_index, make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/films/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
