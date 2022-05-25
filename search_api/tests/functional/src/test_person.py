from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_person(create_index, make_get_request, test_data):
    person_test_data = await test_data("persons")
    for i in range(len(person_test_data)):
        tested_person = person_test_data[i]
        tested_person["film_works"] = [
            {
                "uuid": _["uuid"],
                "title": _["title"],
                "imdb_rating": float(_["imdb_rating"]),
                "role": _["role"],
            }
            for _ in tested_person["film_works"]
        ]
        response = await make_get_request(
            f"/persons/{tested_person['uuid']}", params={}
        )
        assert response.status == HTTPStatus.OK
        assert response.body == tested_person


@pytest.mark.asyncio
async def test_person_not_found(create_index, make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/persons/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
