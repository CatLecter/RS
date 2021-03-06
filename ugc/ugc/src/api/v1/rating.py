import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ...schemas import RatingMessage
from ...services import RatingService
from ...services.getters import get_rating_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/movies/{movie_uuid}/rating")
async def process_like_message(
    msg: RatingMessage,
    movie_uuid: UUID,
    request: Request,
    rating_service: RatingService = Depends(get_rating_service),
):
    """Rating a movie."""
    value = {
        "user_uuid": request.state.user_uuid,
        "movie_uuid": movie_uuid,
        "datetime": msg.datetime,
        "rating": msg.rating,
    }
    await rating_service.send(value)
    return {
        "success": {
            "User UUID": request.state.user_uuid,
            "Movie UUID": movie_uuid,
            "Rating": msg.rating,
        }
    }
