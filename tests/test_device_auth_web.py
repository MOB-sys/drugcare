"""DeviceAuth 웹 세션 테스트 — 쿠키 폴백, 세션 생성, 면제 경로."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_exempt_prefix_drugs_slugs(client):
    """EXEMPT_PREFIXES: /drugs/slugs 인증 없이 통과."""
    with patch(
        "src.backend.services.drug_service.get_all_drug_slugs",
        new_callable=AsyncMock,
        return_value=[],
    ):
        resp = await client.get("/api/v1/drugs/slugs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_exempt_prefix_supplements_by_slug(client):
    """EXEMPT_PREFIXES: /supplements/by-slug/ 인증 없이 통과."""
    with patch(
        "src.backend.services.supplement_service.get_supplement_by_slug",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.get("/api/v1/supplements/by-slug/supp-1")
    # 404 는 인증 통과 후 데이터 없음 → 인증 자체는 통과
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_web_session_cookie_created(client):
    """X-Device-ID 없고 session_id 쿠키 없으면 새 세션 쿠키 생성."""
    with patch(
        "src.backend.services.drug_service.search_drugs",
        new_callable=AsyncMock,
        return_value={"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0},
    ):
        resp = await client.get("/api/v1/drugs/search?q=test")
    assert resp.status_code == 200
    # Set-Cookie 헤더에 session_id가 포함되어야 함
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session_id=" in set_cookie
    assert "web-" in set_cookie


@pytest.mark.asyncio
async def test_web_session_cookie_reused(client):
    """session_id 쿠키가 있으면 재사용 (새 쿠키 미생성)."""
    with patch(
        "src.backend.services.drug_service.search_drugs",
        new_callable=AsyncMock,
        return_value={"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0},
    ):
        resp = await client.get(
            "/api/v1/drugs/search?q=test",
            cookies={"session_id": "web-existing-session"},
        )
    assert resp.status_code == 200
    # 기존 쿠키 사용 시 새 쿠키 미생성
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session_id=" not in set_cookie


@pytest.mark.asyncio
async def test_header_device_id_takes_precedence(client, auth_headers):
    """X-Device-ID 헤더가 있으면 쿠키보다 우선."""
    with patch(
        "src.backend.services.drug_service.search_drugs",
        new_callable=AsyncMock,
        return_value={"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0},
    ):
        resp = await client.get(
            "/api/v1/drugs/search?q=test",
            headers=auth_headers,
            cookies={"session_id": "web-should-not-use"},
        )
    assert resp.status_code == 200
    # 헤더 사용 시 새 쿠키 미생성
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session_id=" not in set_cookie


@pytest.mark.asyncio
async def test_health_endpoint_exempt(client):
    """EXEMPT_PATHS: /health 인증 없이 통과."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
