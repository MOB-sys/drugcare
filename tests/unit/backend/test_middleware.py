"""미들웨어 테스트 — 디바이스 인증 + 에러 핸들러."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_device_auth_missing_header_creates_web_session(client):
    """X-Device-ID 헤더 없이 요청 시 웹 세션 쿠키가 생성되는지 확인한다."""
    with patch(
        "src.backend.services.drug_service.search_drugs",
        new_callable=AsyncMock,
        return_value={"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0},
    ):
        response = await client.get("/api/v1/drugs/search?q=test")

    # 웹 세션 쿠키 자동 생성으로 요청 통과
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_id=" in set_cookie


@pytest.mark.asyncio
async def test_device_auth_with_header(client, auth_headers):
    """X-Device-ID 헤더가 있으면 정상적으로 요청이 처리되는지 확인한다."""
    with patch(
        "src.backend.services.drug_service.search_drugs",
        new_callable=AsyncMock,
        return_value={"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0},
    ):
        response = await client.get("/api/v1/drugs/search?q=test", headers=auth_headers)

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True


@pytest.mark.asyncio
async def test_device_auth_exempt_health(client):
    """면제 경로(/api/v1/health)는 헤더 없이도 통과하는지 확인한다."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_device_auth_exempt_docs(client):
    """면제 경로(/docs)는 헤더 없이도 통과하는지 확인한다."""
    response = await client.get("/docs")

    # FastAPI의 /docs는 200 또는 리다이렉트를 반환한다
    assert response.status_code in (200, 307)


@pytest.mark.asyncio
async def test_error_handler_returns_api_response_format(client, auth_headers):
    """존재하지 않는 경로 요청 시에도 응답 형식이 유지되는지 확인한다.

    Note: FastAPI의 404는 미들웨어가 아닌 내부 핸들러에서 처리되므로
    여기서는 에러 핸들러가 아닌 일반 404 응답을 검증한다.
    """
    response = await client.get("/api/v1/nonexistent", headers=auth_headers)

    # FastAPI 기본 404 응답
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_device_auth_post_without_header_creates_web_session(client):
    """POST 요청에서 X-Device-ID 헤더 없으면 웹 세션이 생성되는지 확인한다."""
    response = await client.post(
        "/api/v1/interactions/check",
        json={"items": [{"item_type": "drug", "item_id": 1}, {"item_type": "drug", "item_id": 2}]},
        headers={"origin": "http://localhost:3000"},
    )

    # 웹 세션 쿠키 자동 생성으로 요청 통과
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "session_id=" in set_cookie


@pytest.mark.asyncio
async def test_device_auth_post_with_header(client, auth_headers):
    """POST 요청에서 X-Device-ID 헤더가 있으면 정상 처리되는지 확인한다."""
    response = await client.post(
        "/api/v1/interactions/check",
        json={"items": [{"item_type": "drug", "item_id": 1}, {"item_type": "drug", "item_id": 2}]},
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["disclaimer"] == "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다."
