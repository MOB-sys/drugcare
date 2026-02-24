"""피드백 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_submit_feedback_success(client, auth_headers):
    """피드백 제출 성공."""
    mock_result = {
        "id": 1,
        "category": "bug",
        "content": "검색 결과가 표시되지 않습니다.",
        "app_version": "1.0.0",
        "created_at": "2026-02-24T09:00:00+00:00",
    }
    with patch(
        "src.backend.routers.feedback.feedback_service.create_feedback",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/feedback",
            json={
                "category": "bug",
                "content": "검색 결과가 표시되지 않습니다.",
                "app_version": "1.0.0",
                "os_info": "iOS 17.0",
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["category"] == "bug"


@pytest.mark.asyncio
async def test_submit_feedback_feature_request(client, auth_headers):
    """기능 제안 피드백 제출 성공."""
    mock_result = {
        "id": 2,
        "category": "feature",
        "content": "약 사진으로 검색하는 기능이 있으면 좋겠습니다.",
        "app_version": "1.0.0",
        "created_at": "2026-02-24T09:00:00+00:00",
    }
    with patch(
        "src.backend.routers.feedback.feedback_service.create_feedback",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/feedback",
            json={
                "category": "feature",
                "content": "약 사진으로 검색하는 기능이 있으면 좋겠습니다.",
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["data"]["category"] == "feature"


@pytest.mark.asyncio
async def test_submit_feedback_data_error(client, auth_headers):
    """데이터 오류 피드백 제출 성공."""
    mock_result = {
        "id": 3,
        "category": "data_error",
        "content": "타이레놀 성분 정보가 잘못된 것 같습니다.",
        "app_version": "1.0.0",
        "created_at": "2026-02-24T09:00:00+00:00",
    }
    with patch(
        "src.backend.routers.feedback.feedback_service.create_feedback",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/feedback",
            json={
                "category": "data_error",
                "content": "타이레놀 성분 정보가 잘못된 것 같습니다.",
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_submit_feedback_too_short(client, auth_headers):
    """내용이 너무 짧으면 422 반환."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "category": "bug",
            "content": "짧음",
        },
        headers=auth_headers,
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_missing_category(client, auth_headers):
    """카테고리 누락 시 422 반환."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "content": "테스트 피드백 내용입니다.",
        },
        headers=auth_headers,
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_feedback_no_device_id(client):
    """X-Device-ID 헤더 없으면 401 반환."""
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "category": "bug",
            "content": "디바이스 ID 없는 요청입니다.",
        },
    )

    assert resp.status_code == 401
