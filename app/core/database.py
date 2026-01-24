from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from core.config import settings
from typing import AsyncGenerator


# Engine
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_size=10,
    max_overflow=10,
)


# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    pass


# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session