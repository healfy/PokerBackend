import os
from pathlib import Path

import backend
from pydantic import BaseModel, BaseSettings


class AuthSettings(BaseModel):
    secret_key: str = "SECRET"
    algorithm: str = "HS256"
    access_token_expires: int = 300
    refresh_token_expires: int = 60 * 24 * 30

    def __hash__(self):
        return hash(self.json())


class PostgresSettings(BaseModel):
    USER: str = os.getenv("POSTGRES_USER", "test")
    PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "test")
    HOST: str = os.getenv("POSTGRES_HOST", "0.0.0.0")
    PORT: int = os.getenv("POSTGRES_PORT", 5432)
    DB: str = os.getenv("POSTGRES_DB", "test")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
        )


class AppSettings(BaseSettings):
    VERSION: str = "0.0.1"
    AUTH: AuthSettings = AuthSettings()
    POSTGRES: PostgresSettings = PostgresSettings()

    def __hash__(self):
        return hash(self.json())
