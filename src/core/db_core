from yarl import URL
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


def make_db_url() -> str:
    return URL.build(
        scheme="postgresql",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        path=f"/{settings.DB_NAME}",
    ).human_repr()


DB_URL: str = make_db_url()
DB_SCHEMA: str = settings.DB_SCHEMA


SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_use_lifo": True,
    "pool_size": 5,
    "max_overflow": 5,
    "pool_timeout": 10,
    "echo": True,
}


engine: Engine = create_engine(
    DB_URL,
    **SQLALCHEMY_ENGINE_OPTIONS,
)


NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(
    schema=DB_SCHEMA,
    naming_convention=NAMING_CONVENTION,
)

class Base(DeclarativeBase):
    metadata = metadata


__all__ = [
    "DB_URL",
    "DB_SCHEMA",
    "engine",
    "Base",
]
