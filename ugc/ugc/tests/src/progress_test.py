import logging
from http import HTTPStatus

import pytest

from ...src.schemas import MovieProgressMessage
from ..testdata import HEADERS, MOVIE_ID, SECONDS_WATCHED

pytestmark = pytest.mark.asyncio
logger = logging.getLogger(__name__)


class TestMovieProgress:
    """Represents movie progress related tests."""

    url = f"/movies/{MOVIE_ID}/view"

    async def test_success(self, make_post_request):
        """Test success case."""
        data = MovieProgressMessage(seconds_watched=SECONDS_WATCHED)
        response = await make_post_request(
            self.url,
            headers=HEADERS,
            data=data.json(),
        )
        logger.debug("Response: %s %s", response.status, response)
        assert response.status == HTTPStatus.OK
