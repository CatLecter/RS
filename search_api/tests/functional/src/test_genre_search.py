from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_genres_all_list(create_index, make_get_request, test_data):
    response = await make_get_request(method="/genres/", params={})
    genres_test_data = await test_data("genres")
    expected_items = [
        {
            "uuid": _["uuid"],
            "name": _["name"],
        }
        for _ in genres_test_data
    ]
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == expected_items
    assert response.body["total"] == len(expected_items)
    assert response.body["page_size"] is None
    assert response.body["page_number"] is None


@pytest.mark.asyncio
async def test_genres_search(create_index, make_get_request, test_data):
    genres_test_data = await test_data("genres")
    expected_items = [
        {
            "uuid": _["uuid"],
            "name": _["name"],
        }
        for _ in genres_test_data
    ]
    for i in range(len(expected_items)):
        tested_genre = expected_items[i]
        response = await make_get_request(
            "/genres/", params={"query": tested_genre["name"]}
        )
        assert response.status == HTTPStatus.OK
        assert response.body["items"][0] == tested_genre


@pytest.mark.asyncio
async def test_genres_search_not_found(create_index, make_get_request):
    response = await make_get_request("/genres/", params={"query": "NotFound"})
    assert response.status == HTTPStatus.OK
    assert response.body["items"] == []
    assert response.body["total"] == 0
    assert response.body["page_size"] is None
    assert response.body["page_number"] is None
