from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], #TODO: Change this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routes
    app.include_router(router)

    return app


router: APIRouter = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "Dispositio backend is running"}


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(api_router, prefix="/api")


app: FastAPI = create_app()

__all__ = ["app"]
