import uvicorn

from core.config import settings
from utils.app import app


def run() -> None:
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.value,
    )


if __name__ == "__main__":
    run()


__all__ = ["app"]
