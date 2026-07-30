import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

logger = logging.getLogger("hiresmart.database")

db_url = settings.DATABASE_URL

# Check if database driver is available; if not, default to sqlite+aiosqlite
try:
    if "mysql" in db_url:
        import aiomysql
    elif "asyncpg" in db_url:
        import asyncpg
except ImportError as err:
    logger.warning(f"Required database driver not found: {err}. Falling back to SQLite async engine.")
    db_url = "sqlite+aiosqlite:///./hiresmart_dev.db"

connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    connect_args=connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing asynchronous database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error(f"Database session error: {exc}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables asynchronously with connection failure fallback."""
    global engine, AsyncSessionLocal
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database connected and tables initialized successfully with engine URL: {engine.url}")
    except Exception as exc:
        logger.warning(f"Primary DB connection ({engine.url}) failed: {exc}. Switching to SQLite local fallback DB.")
        db_url_fallback = "sqlite+aiosqlite:///./hiresmart_dev.db"
        engine = create_async_engine(
            db_url_fallback,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
            future=True,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite local fallback database initialized successfully.")

