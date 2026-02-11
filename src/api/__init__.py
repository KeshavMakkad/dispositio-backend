from fastapi import APIRouter

from api.v1 import router as v1_router

router: APIRouter = APIRouter()

router.include_router(v1_router, prefix="/v1", tags=["v1"])

__all__ = ["router"]