from api.v1 import router as v1_router
from fastapi import APIRouter

router = APIRouter(prefix="/rs/api")
router.include_router(v1_router)
