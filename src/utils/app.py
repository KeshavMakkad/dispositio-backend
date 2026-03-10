from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TEMP: allow all (tighten later)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(router)

    return app


router: APIRouter = APIRouter()
router.include_router(api_router, prefix="/api")


app: FastAPI = create_app()

__all__ = ["app"]
