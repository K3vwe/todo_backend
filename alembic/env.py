# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Load app settings and models AFTER .env
from app.core.config import settings
from app.core.database import Base  # Your SQLAlchemy Base
import app.models  # Ensure all models are imported

# ---------------- Alembic Config ---------------- #
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------- Metadata ---------------- #
target_metadata = Base.metadata

# ---------------- Database URL ---------------- #
db_url = settings.SQLALCHEMY_DATABASE_URI
config.set_main_option("sqlalchemy.url", db_url)
print("Alembic connecting to:", db_url)

# ---------------- Offline Migrations ---------------- #
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------- Online Migrations ---------------- #
def do_run_migrations(sync_connection):
    """Run sync migrations inside async engine."""
    context.configure(
        connection=sync_connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Async engine + sync migration bridge."""
    async_engine = create_async_engine(db_url, poolclass=pool.NullPool)
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await async_engine.dispose()


# ---------------- Entry Point ---------------- #
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
