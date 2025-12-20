from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from app.config import settings
from typing import AsyncGenerator


# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=False,  # Set to True to see SQL queries (useful for debugging)
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes
    Provides a database session and ensures it's closed after use

    Usage in FastAPI:
        @app.get("/models")
        async def get_models(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Initialize database tables
    Only use in development - in production, use Alembic migrations
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
