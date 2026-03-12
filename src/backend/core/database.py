"""SQLAlchemy async engine + session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.backend.core.config import get_settings

settings = get_settings()

_connect_args: dict = {"timeout": 10}
# SSL은 DATABASE_URL의 ?ssl= 파라미터로 제어 (Docker 내부 통신은 SSL 불필요)
if "ssl=" in settings.DATABASE_URL:
    _connect_args["ssl"] = settings.DATABASE_URL.split("ssl=")[-1].split("&")[0]

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    connect_args=_connect_args,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성 — 요청별 DB 세션 제공."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
