from enum import StrEnum, auto
from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory (parent of src)
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Environment(StrEnum):
    dev = auto()
    stg = auto()
    prod = auto()


class LogLevel(StrEnum):
    debug = auto()
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()


class GlobalConfig(BaseSettings):
    ENVIRONMENT: Environment = Field(default=Environment.dev)

    LOG_LEVEL: LogLevel = Field(default=LogLevel.debug)
    RELOAD: bool = Field(default=True)

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=3000)

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_SCHEMA: str
    DB_PASSWORD: str = Field(default="")

    # Supports legacy CREARE_MODELS for backward compatibility.
    CREATE_MODELS: bool = Field(
        validation_alias=AliasChoices("CREATE_MODELS", "CREARE_MODELS")
    )

    # Backend JWT settings. Supports legacy SUPABASE_JWT_SECRET env for compatibility.
    JWT_SECRET: str = Field(
        validation_alias=AliasChoices("JWT_SECRET", "SUPABASE_JWT_SECRET")
    )
    SUPABASE_JWT_SECRET: str | None = Field(default=None)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Auth cookie configuration.
    COOKIE_SECURE: bool = Field(default=False)
    COOKIE_SAMESITE: str = Field(default="lax")
    COOKIE_DOMAIN: str | None = Field(default=None)

    # Viewer can access seating plan only after exam_time - this offset (minutes).
    SEATING_VIEWER_ACCESS_TIME_DIFF_MINUTES: int = Field(default=30)

    # Shared secret for non-interactive Google Sheets integration.
    SHEETS_API_KEY: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_ignore_empty=True, extra="ignore"
    )


settings: GlobalConfig = GlobalConfig()

__all__ = ["settings"]
