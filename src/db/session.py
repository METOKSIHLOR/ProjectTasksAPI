from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession

from src.config.config import config
from src.db.models import Base

engine: AsyncEngine | None = None
SessionFactory: async_sessionmaker[AsyncSession] | None = None

async def connect_db():
    global engine, SessionFactory
    engine = create_async_engine(
        url=config.postrges.url,
        pool_pre_ping=True,
    )

    SessionFactory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    if engine:
        #async with engine.begin() as conn:
        #    await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()