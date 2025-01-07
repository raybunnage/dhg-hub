from dataclasses import dataclass
from functools import lru_cache
from pydantic_settings import BaseSettings


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration."""

    url: str
    max_connections: int = 10
    timeout: int = 30


class Settings(BaseSettings):
    """Application settings."""

    database: DatabaseConfig
    debug: bool = False
