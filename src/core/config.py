from enum import StrEnum, auto
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    DB_PASSWORD: str


    CREARE_MODELS: bool
    
    model_config = SettingsConfigDict (
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings: GlobalConfig = ()

__all__ = ["settings"]