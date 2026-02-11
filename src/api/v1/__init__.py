from fastapi import APIRouter

from api.v1.classroom import router as classroom_router
from api.v1.seating import router as seating_router

router: APIRouter = APIRouter()

router.include_router(classroom_router, prefix="/classroom", tags=["classroom"])
router.include_router(seating_router, prefix="/seating", tags=["seating"])

_all__ = ["router"]