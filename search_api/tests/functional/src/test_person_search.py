import math
from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_persons_search(create_index, make_get_request, test_data):
    persons_test_data = await test_data("persons")
    expected_items = [
        {
            "uuid": _["uuid"],
            "full_name": _["full_name"],
        }
        for _ in persons_test_data
    ]
    for i in range(len(expected_items)):
        tested_persons = expected_items[i]
        response = await make_get_request(
            "/persons/search/", params={"query": tested_persons["full_name"]}
        )
        assert response.status == HTTPStatus.OK
        assert response.body["items"][0] == tested_persons


@pytest.mark.asyncio
async def test_persons_search_not_found(create_index, make_get_request):
    response = await make_get_request("/persons/search/", params={"query": "NotFound"})
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == []
    assert response.body["total"] == 0
    assert response.body["page_size"] == 20
    assert response.body["page_number"] == 1


@pytest.mark.asyncio
async def test_persons_pagination(create_index, make_get_request, test_data):
    persons_test_data = await test_data("persons")
    page_size = 20
    pages = math.ceil(len(persons_test_data) / page_size)
    for page in range(1, pages):
        response = await make_get_request(
            "/persons/search/", params={"page[number]": page, "page[size]": page_size}
        )
        assert response.status == HTTPStatus.OK
        assert response.body["total"] == 65
        assert response.body["page_size"] == page_size
        assert response.body["page_number"] == page


@pytest.mark.asyncio
async def test_persons_all(create_index, make_get_request, test_data):
    persons_test_data = await test_data("persons")
    expected_items = [
        {
            "uuid": _["uuid"],
            "full_name": _["full_name"],
        }
        for _ in persons_test_data
    ]
    response = await make_get_request(
        "/persons/search/", params={"page[number]": 1, "page[size]": 65}
    )
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == expected_items
    assert response.body["total"] == 65
    assert response.body["page_size"] == 65
    assert response.body["page_number"] == 1
