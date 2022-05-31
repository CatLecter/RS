import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ...schemas import MovieProgressMessage
from ...services import ViewService
from ...services.getters import get_view_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/movies/{movie_uuid}/view")
async def track_movie_progress(
    msg: MovieProgressMessage,
    movie_uuid: UUID,
    request: Request,
    view_service: ViewService = Depends(get_view_service),
):
    """Track movie progress."""
    value = {
        "user_uuid": request.state.user_uuid,
        "movie_uuid": movie_uuid,
        "datetime": msg.datetime,
        "progress": msg.progress,
    }
    await view_service.send(value)
    return {
        "success": {
            "User UUID": request.state.user_uuid,
            "Movie UUID": movie_uuid,
            "Progress": msg.progress,
        }
    }
