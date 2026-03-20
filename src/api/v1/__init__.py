from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.classroom import router as classroom_router
from api.v1.seating import router as seating_router
from api.v1.user import router as user_router

router: APIRouter = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(classroom_router, prefix="/classroom", tags=["classroom"])
router.include_router(seating_router, prefix="/seating", tags=["seating"])

__all__ = ["router"]
