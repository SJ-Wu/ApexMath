"""資料庫引擎：建立 async engine 與 session factory。"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.async_database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI 依賴注入用：提供一個 async DB session，請求結束後自動關閉。"""
    async with async_session_factory() as session:
        yield session
