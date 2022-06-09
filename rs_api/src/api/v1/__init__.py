from api.v1.rs_movies import router as rs_movies
from fastapi import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(rs_movies)
