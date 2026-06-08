"""
PostgreSQL connection scaffolding using SQLAlchemy Async Session support.
This provides async connection pooling, sessions, and transaction controls,
supporting local development first, with plans to scale to Azure Database for PostgreSQL.
"""

import logging
from collections.abc import AsyncGenerator
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

logger = logging.getLogger(__name__)

# Create Async Engine with pooling configurations.
# Azure DB for PostgreSQL may require custom sslmode settings in production.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "local",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Proactively verify connections to handle restarts/Azure failovers
)

# Create SessionMaker bound to the async engine
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Declarative base class for models
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an asynchronous database session.
    Automatically handles rollback on exceptions and final clean up.
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error("Database session transaction error: %s. Rolling back.", str(e))
            await session.rollback()
            raise
        finally:
            await session.close()
