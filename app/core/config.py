# app/core/config.py
from typing import Any, Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl, HttpUrl
from pydantic.functional_validators import BeforeValidator
from sqlalchemy.engine import URL
import os


def parse_cors(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
    if isinstance(v, list):
        return [str(i).rstrip("/") for i in v]
    raise ValueError("Invalid CORS origins")


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


    # Project
    PROJECT_NAME: str

    # Security
    SECRET_KEY: str

    # Frontend
    FRONTEND_HOST: AnyUrl

    # Observability
    SENTRY_DSN: HttpUrl | None = None

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        str | list[str],
        BeforeValidator(parse_cors),
    ] = Field(default="")

    @property
    def all_cors_origins(self) -> list[str]:
        return self.BACKEND_CORS_ORIGINS + [str(self.FRONTEND_HOST).rstrip("/")]

    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # asyncpg connection
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # @property
    # def SQLALCHEMY_DATABASE_URI(self) -> str:
    #     return str(
    #         URL.create(
    #             drivername="postgresql+asyncpg",
    #             username=self.POSTGRES_USER,
    #             password=self.POSTGRES_PASSWORD,
    #             host=self.POSTGRES_SERVER,
    #             port=self.POSTGRES_PORT,
    #             database=self.POSTGRES_DB,
    #         )
    #     )


print("POSTGRES_PASSWORD FROM ENV:", repr(os.getenv("POSTGRES_PASSWORD")))
settings = Settings()