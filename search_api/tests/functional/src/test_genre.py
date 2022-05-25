from http import HTTPStatus
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_genre(create_index, make_get_request, test_data):
    expected_result = await test_data("genres")
    for i in range(len(expected_result)):
        tested_genre = expected_result[i]
        response = await make_get_request(f"/genres/{tested_genre['uuid']}", params={})
        assert response.status == HTTPStatus.OK
        assert response.body == tested_genre


@pytest.mark.asyncio
async def test_genre_not_found(create_index, make_get_request):
    _uuid = uuid4()
    response = await make_get_request(f"/genres/{_uuid}", params={})
    assert response.status == HTTPStatus.NOT_FOUND
