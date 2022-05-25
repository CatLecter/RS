from fastapi import APIRouter

from . import v1

router = APIRouter(prefix="/ugc/api")

router.include_router(v1.router)
