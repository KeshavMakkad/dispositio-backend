from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # TEMP: allow all (tighten later)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app: FastAPI = create_app()

__all__ = ["app"]
