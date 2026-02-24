"""테스트 공통 픽스처 — httpx AsyncClient + 의존성 오버라이드."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.main import app


TEST_DEVICE_ID = "test-device-550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def device_id() -> str:
    """테스트용 디바이스 UUID를 반환한다."""
    return TEST_DEVICE_ID


@pytest.fixture
def auth_headers(device_id: str) -> dict[str, str]:
    """X-Device-ID 헤더가 포함된 dict를 반환한다.

    Args:
        device_id: 테스트용 디바이스 UUID.

    Returns:
        인증 헤더 dict.
    """
    return {"X-Device-ID": device_id}


def _create_mock_db_session() -> AsyncMock:
    """테스트용 모의 DB 세션을 생성한다.

    Returns:
        AsyncMock DB 세션.
    """
    mock_session = AsyncMock()
    # SELECT 1 결과를 모의한다
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_session.execute.return_value = mock_result
    return mock_session


def _create_mock_redis() -> AsyncMock:
    """테스트용 모의 Redis 클라이언트를 생성한다.

    Returns:
        AsyncMock Redis 클라이언트.
    """
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    return mock_redis


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """httpx AsyncClient 픽스처 — 의존성 오버라이드 적용.

    DB와 Redis 의존성을 모의 객체로 교체한다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = _create_mock_db_session()
    mock_redis = _create_mock_redis()

    async def override_get_db() -> AsyncGenerator:
        """모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_db_error() -> AsyncGenerator[httpx.AsyncClient, None]:
    """DB 에러 상태의 httpx AsyncClient 픽스처.

    DB execute가 예외를 발생시키도록 설정된다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB connection failed")

    mock_redis = _create_mock_redis()

    async def override_get_db() -> AsyncGenerator:
        """에러 모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_redis_error() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Redis 에러 상태의 httpx AsyncClient 픽스처.

    Redis ping이 예외를 발생시키도록 설정된다.

    Yields:
        httpx.AsyncClient 인스턴스.
    """
    mock_db = _create_mock_db_session()

    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Redis connection failed")

    async def override_get_db() -> AsyncGenerator:
        """모의 DB 세션 의존성."""
        yield mock_db

    def override_get_redis() -> AsyncMock:
        """에러 모의 Redis 클라이언트 의존성."""
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
