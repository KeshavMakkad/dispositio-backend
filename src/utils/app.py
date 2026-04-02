import logging
from logging.config import dictConfig

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from core.config import settings


def configure_logging() -> None:
    log_level_name = settings.LOG_LEVEL.value.upper()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": log_level_name,
            },
            "loggers": {
                "uvicorn": {"level": log_level_name},
                "uvicorn.error": {"level": log_level_name},
                "uvicorn.access": {"level": log_level_name},
            },
        }
    )
    logging.getLogger(__name__).warning(
        "Logging configured with level=%s (env keys: LOG_LEVEL/LOGS)",
        settings.LOG_LEVEL.value,
    )


def create_app() -> FastAPI:
    configure_logging()
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
