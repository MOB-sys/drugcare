"""RequestLoggerMiddleware 단위 테스트 — 요청 UUID 및 로깅 검증."""

import logging
import uuid

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.backend.middleware.request_logger import RequestLoggerMiddleware


# ---------------------------------------------------------------------------
# 테스트용 미니 FastAPI 앱
# ---------------------------------------------------------------------------

_test_app = FastAPI()
_test_app.add_middleware(RequestLoggerMiddleware)


@_test_app.get("/ping")
async def _route_ping():
    """테스트 엔드포인트."""
    return {"pong": True}


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def log_client():
    """RequestLoggerMiddleware가 적용된 테스트 클라이언트를 생성한다."""
    transport = httpx.ASGITransport(app=_test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# 테스트: X-Request-ID 헤더 존재
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_id_header_present(log_client: httpx.AsyncClient):
    """응답에 X-Request-ID 헤더가 존재한다."""
    resp = await log_client.get("/ping")
    assert "x-request-id" in resp.headers


# ---------------------------------------------------------------------------
# 테스트: X-Request-ID가 유효한 UUID 형식
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_id_is_valid_uuid(log_client: httpx.AsyncClient):
    """X-Request-ID 값이 유효한 UUID4 형식이다."""
    resp = await log_client.get("/ping")
    request_id = resp.headers["x-request-id"]
    parsed = uuid.UUID(request_id, version=4)
    assert str(parsed) == request_id


# ---------------------------------------------------------------------------
# 테스트: 매 요청마다 다른 UUID 생성
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unique_request_ids(log_client: httpx.AsyncClient):
    """각 요청마다 서로 다른 X-Request-ID가 생성된다."""
    resp1 = await log_client.get("/ping")
    resp2 = await log_client.get("/ping")
    assert resp1.headers["x-request-id"] != resp2.headers["x-request-id"]


# ---------------------------------------------------------------------------
# 테스트: 구조화된 로그 기록 확인
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_contains_structured_info(log_client: httpx.AsyncClient, caplog):
    """로그에 method, path, status, duration_ms, request_id가 포함된다."""
    with caplog.at_level(logging.INFO, logger="src.backend.middleware.request_logger"):
        resp = await log_client.get("/ping")

    request_id = resp.headers["x-request-id"]
    log_message = caplog.text

    assert "method=GET" in log_message
    assert "path=/ping" in log_message
    assert "status=200" in log_message
    assert "duration_ms=" in log_message
    assert request_id in log_message
