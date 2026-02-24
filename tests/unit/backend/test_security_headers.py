"""SecurityHeadersMiddleware 단위 테스트 — 보안 헤더 추가 검증."""

from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from src.backend.middleware.security_headers import SecurityHeadersMiddleware


# ---------------------------------------------------------------------------
# 테스트용 미니 FastAPI 앱
# ---------------------------------------------------------------------------

_test_app = FastAPI()
_test_app.add_middleware(SecurityHeadersMiddleware)


@_test_app.get("/ping")
async def _route_ping():
    """테스트 엔드포인트."""
    return {"pong": True}


# ---------------------------------------------------------------------------
# 픽스처
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def sec_client():
    """SecurityHeadersMiddleware가 적용된 테스트 클라이언트를 생성한다."""
    transport = httpx.ASGITransport(app=_test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# 테스트: 기본 보안 헤더 존재 확인
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_x_content_type_options(sec_client: httpx.AsyncClient):
    """X-Content-Type-Options: nosniff 헤더가 존재한다."""
    resp = await sec_client.get("/ping")
    assert resp.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
async def test_x_frame_options(sec_client: httpx.AsyncClient):
    """X-Frame-Options: DENY 헤더가 존재한다."""
    resp = await sec_client.get("/ping")
    assert resp.headers["x-frame-options"] == "DENY"


@pytest.mark.asyncio
async def test_x_xss_protection(sec_client: httpx.AsyncClient):
    """X-XSS-Protection 헤더가 존재한다."""
    resp = await sec_client.get("/ping")
    assert resp.headers["x-xss-protection"] == "1; mode=block"


@pytest.mark.asyncio
async def test_referrer_policy(sec_client: httpx.AsyncClient):
    """Referrer-Policy 헤더가 존재한다."""
    resp = await sec_client.get("/ping")
    assert resp.headers["referrer-policy"] == "strict-origin-when-cross-origin"


# ---------------------------------------------------------------------------
# 테스트: HSTS — 개발 환경에서는 제외
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.security_headers.get_settings")
async def test_hsts_excluded_in_development(mock_settings, sec_client: httpx.AsyncClient):
    """개발 환경에서는 Strict-Transport-Security 헤더가 없다."""
    mock_settings.return_value.is_development = True
    resp = await sec_client.get("/ping")
    assert "strict-transport-security" not in resp.headers


# ---------------------------------------------------------------------------
# 테스트: HSTS — 프로덕션 환경에서 포함
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("src.backend.middleware.security_headers.get_settings")
async def test_hsts_included_in_production(mock_settings, sec_client: httpx.AsyncClient):
    """프로덕션 환경에서는 Strict-Transport-Security 헤더가 포함된다."""
    mock_settings.return_value.is_development = False
    resp = await sec_client.get("/ping")
    assert "strict-transport-security" in resp.headers
    assert "max-age=31536000" in resp.headers["strict-transport-security"]
