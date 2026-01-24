from typing import Any, Annotated
from pydantic import AnyUrl, HttpUrl, PostgresDsn, Field
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        list[str],
        BeforeValidator(parse_cors),
    ] = Field(default_factory=list)

    @property
    def all_cors_origins(self) -> list[str]:
        return self.BACKEND_CORS_ORIGINS + [str(self.FRONTEND_HOST).rstrip("/")]

    # Database (components)
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Observability
    SENTRY_DSN: HttpUrl | None = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}",
        )


settings = Settings()
