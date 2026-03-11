"""RateLimiterMiddleware 단위 테스트 — Redis 기반 레이트 리밋 검증."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.backend.middleware.rate_limiter import RateLimiterMiddleware


# ---------------------------------------------------------------------------
# 테스트용 미니 FastAPI 앱
# ---------------------------------------------------------------------------

_test_app = FastAPI()
_test_app.add_middleware(RateLimiterMiddleware)


@_test_app.get("/api/v1/health")
async def _route_health():
    """면제 경로 — 헬스체크."""
    return {"status": "ok"}


@_test_app.get("/api/v1/drugs/search")
async def _route_search():
    """검색 엔드포인트 (레이트 리밋 면제)."""
    return {"results": []}


@_test_app.get("/api/v1/cabinet")
async def _route_cabinet():
    """캐비넷 엔드포인트 (레이트 리밋 적용)."""
    return {"items": []}


@_test_app.post("/api/v1/interactions/check")
async def _route_mutation():
    """뮤테이션 엔드포인트."""
    return {"checked": True}


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def rate_client():
    """RateLimiterMiddleware가 적용된 테스트 클라이언트를 생성한다."""
    transport = httpx.ASGITransport(app=_test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# 테스트: 제한 이내 요청 통과
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.rate_limiter.get_redis")
async def test_under_limit_passes(mock_get_redis, rate_client: httpx.AsyncClient):
    """레이트 리밋 이내의 요청은 정상 통과한다."""
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    mock_get_redis.return_value = mock_redis

    resp = await rate_client.get("/api/v1/drugs/search")
    assert resp.status_code == 200
    assert resp.json()["results"] == []


# ---------------------------------------------------------------------------
# 테스트: 검색 제한 초과 → 429
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.rate_limiter.get_redis")
async def test_search_over_limit_returns_429(
    mock_get_redis, rate_client: httpx.AsyncClient
):
    """레이트 리밋 초과 시 429를 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 61
    mock_get_redis.return_value = mock_redis

    resp = await rate_client.get("/api/v1/cabinet")
    assert resp.status_code == 429

    body = resp.json()
    assert body["success"] is False
    assert "요청 한도" in body["error"]


# ---------------------------------------------------------------------------
# 테스트: 뮤테이션 제한 초과 → 429
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.rate_limiter.get_redis")
async def test_mutation_over_limit_returns_429(
    mock_get_redis, rate_client: httpx.AsyncClient
):
    """뮤테이션 API 31번째 요청은 429를 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 31
    mock_get_redis.return_value = mock_redis

    resp = await rate_client.post("/api/v1/interactions/check")
    assert resp.status_code == 429


# ---------------------------------------------------------------------------
# 테스트: 면제 경로는 레이트 리밋 검사 안 함
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_exempt_path_bypasses_rate_limit(rate_client: httpx.AsyncClient):
    """면제 경로(/api/v1/health)는 Redis 호출 없이 통과한다."""
    resp = await rate_client.get("/api/v1/health")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 테스트: Redis 장애 시 graceful degradation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.rate_limiter.get_redis")
async def test_redis_failure_passes_through(
    mock_get_redis, rate_client: httpx.AsyncClient
):
    """Redis 연결 실패 시 요청을 통과시킨다."""
    mock_redis = AsyncMock()
    mock_redis.incr.side_effect = ConnectionError("Redis unavailable")
    mock_get_redis.return_value = mock_redis

    resp = await rate_client.get("/api/v1/drugs/search")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 테스트: 첫 요청 시 TTL 설정
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.rate_limiter.get_redis")
async def test_first_request_sets_ttl(mock_get_redis, rate_client: httpx.AsyncClient):
    """첫 번째 요청(count=1) 시 Redis 키에 TTL 60초를 설정한다."""
    mock_redis = AsyncMock()
    mock_redis.incr.return_value = 1
    mock_get_redis.return_value = mock_redis

    await rate_client.get("/api/v1/cabinet")

    mock_redis.expire.assert_called_once()
    args = mock_redis.expire.call_args[0]
    assert args[1] == 60
