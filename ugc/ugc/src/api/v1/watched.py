import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.requests import Request

from ...schemas import WatchedMessage
from ...services import WatchService
from ...services.getters import get_watch_service

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/movies/{movie_uuid}/watched")
async def watched_movies(
    msg: WatchedMessage,
    movie_uuid: UUID,
    request: Request,
    watch_service: WatchService = Depends(get_watch_service),
):
    """Add viewed movie."""

    value = {
        "user_uuid": request.state.user_uuid,
        "movie_uuid": movie_uuid,
        "added": msg.added,
        "datetime": msg.datetime,
    }
    await watch_service.send(value)
    return {
        "success": {
            "User UUID": request.state.user_uuid,
            "Movie UUID": movie_uuid,
        }
    }
