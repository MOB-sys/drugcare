"""상호작용 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


DISCLAIMER = "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다."


@pytest.mark.asyncio
async def test_check_interactions_success(client, auth_headers):
    """상호작용 체크 성공 시 결과 반환."""
    mock_result = {
        "total_checked": 1,
        "interactions_found": 1,
        "has_danger": False,
        "results": [
            {
                "item_a_name": "A",
                "item_b_name": "B",
                "severity": "warning",
                "description": "test",
                "mechanism": None,
                "recommendation": None,
                "source": "DUR",
                "evidence_level": None,
            },
        ],
        "disclaimer": DISCLAIMER,
    }
    with patch(
        "src.backend.routers.interactions.interaction_service.check_interactions",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/interactions/check",
            json={
                "items": [
                    {"item_type": "drug", "item_id": 1},
                    {"item_type": "drug", "item_id": 2},
                ],
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["interactions_found"] == 1


@pytest.mark.asyncio
async def test_check_interactions_empty_result(client, auth_headers):
    """상호작용이 없는 경우 interactions_found 가 0."""
    mock_result = {
        "total_checked": 1,
        "interactions_found": 0,
        "has_danger": False,
        "results": [],
        "disclaimer": DISCLAIMER,
    }
    with patch(
        "src.backend.routers.interactions.interaction_service.check_interactions",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/interactions/check",
            json={
                "items": [
                    {"item_type": "drug", "item_id": 1},
                    {"item_type": "drug", "item_id": 2},
                ],
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["data"]["interactions_found"] == 0


@pytest.mark.asyncio
async def test_check_interactions_has_danger(client, auth_headers):
    """위험 상호작용 포함 시 has_danger 가 True."""
    mock_result = {
        "total_checked": 1,
        "interactions_found": 1,
        "has_danger": True,
        "results": [
            {
                "item_a_name": "A",
                "item_b_name": "B",
                "severity": "danger",
                "description": "병용금기",
                "mechanism": None,
                "recommendation": None,
                "source": "DUR",
                "evidence_level": "official",
            },
        ],
        "disclaimer": DISCLAIMER,
    }
    with patch(
        "src.backend.routers.interactions.interaction_service.check_interactions",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/interactions/check",
            json={
                "items": [
                    {"item_type": "drug", "item_id": 1},
                    {"item_type": "drug", "item_id": 2},
                ],
            },
            headers=auth_headers,
        )

    assert resp.json()["data"]["has_danger"] is True


@pytest.mark.asyncio
async def test_check_interactions_min_items_validation(client, auth_headers):
    """최소 2개 아이템 미달 시 422 Validation Error 반환."""
    resp = await client.post(
        "/api/v1/interactions/check",
        json={
            "items": [{"item_type": "drug", "item_id": 1}],
        },
        headers=auth_headers,
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_check_interactions_disclaimer(client, auth_headers):
    """응답에 면책조항이 포함되어야 한다."""
    mock_result = {
        "total_checked": 1,
        "interactions_found": 0,
        "has_danger": False,
        "results": [],
        "disclaimer": DISCLAIMER,
    }
    with patch(
        "src.backend.routers.interactions.interaction_service.check_interactions",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/interactions/check",
            json={
                "items": [
                    {"item_type": "drug", "item_id": 1},
                    {"item_type": "supplement", "item_id": 1},
                ],
            },
            headers=auth_headers,
        )

    assert "의사/약사" in resp.json()["data"]["disclaimer"]


@pytest.mark.asyncio
async def test_check_interactions_no_auth_creates_web_session(client):
    """인증 헤더 없이 요청 시 웹 세션 생성 후 처리."""
    mock_result = {
        "total_checked": 1,
        "interactions_found": 0,
        "has_danger": False,
        "results": [],
        "disclaimer": DISCLAIMER,
    }
    with patch(
        "src.backend.routers.interactions.interaction_service.check_interactions",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/interactions/check",
            json={
                "items": [
                    {"item_type": "drug", "item_id": 1},
                    {"item_type": "drug", "item_id": 2},
                ],
            },
            headers={"origin": "http://localhost:3000"},
        )

    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session_id=" in set_cookie
