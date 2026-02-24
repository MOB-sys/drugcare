"""메트릭스 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_record_metric_event_success(client, auth_headers):
    """메트릭 이벤트 기록 성공."""
    mock_result = {
        "id": 1,
        "event_type": "app_open",
        "created_at": "2026-02-24T09:00:00+00:00",
    }
    with patch(
        "src.backend.routers.metrics.metrics_service.record_event",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/metrics/event",
            json={
                "event_type": "app_open",
                "event_data": {"screen": "home"},
                "app_version": "1.0.0",
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["event_type"] == "app_open"


@pytest.mark.asyncio
async def test_record_interaction_check_event(client, auth_headers):
    """상호작용 체크 이벤트 기록 성공."""
    mock_result = {
        "id": 2,
        "event_type": "interaction_check",
        "created_at": "2026-02-24T09:00:00+00:00",
    }
    with patch(
        "src.backend.routers.metrics.metrics_service.record_event",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/metrics/event",
            json={
                "event_type": "interaction_check",
                "event_data": {"item_count": 3},
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["data"]["event_type"] == "interaction_check"


@pytest.mark.asyncio
async def test_record_event_missing_type(client, auth_headers):
    """event_type 누락 시 422 반환."""
    resp = await client.post(
        "/api/v1/metrics/event",
        json={
            "event_data": {"screen": "home"},
        },
        headers=auth_headers,
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_record_event_no_device_id(client):
    """X-Device-ID 헤더 없으면 401 반환."""
    resp = await client.post(
        "/api/v1/metrics/event",
        json={
            "event_type": "app_open",
        },
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_dashboard_success(client, auth_headers):
    """Kill Criteria 대시보드 조회 성공."""
    mock_result = {
        "period_days": 30,
        "total_devices": 150,
        "active_devices_7d": 45,
        "total_interaction_checks": 320,
        "weekly_interaction_checks": 85,
        "total_feedbacks": 12,
        "avg_events_per_device": 2.13,
    }
    with patch(
        "src.backend.routers.metrics.metrics_service.get_dashboard",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.get(
            "/api/v1/metrics/dashboard?period_days=30",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["total_devices"] == 150
    assert data["data"]["weekly_interaction_checks"] == 85


@pytest.mark.asyncio
async def test_get_dashboard_custom_period(client, auth_headers):
    """커스텀 기간 대시보드 조회."""
    mock_result = {
        "period_days": 7,
        "total_devices": 30,
        "active_devices_7d": 30,
        "total_interaction_checks": 60,
        "weekly_interaction_checks": 60,
        "total_feedbacks": 3,
        "avg_events_per_device": 2.0,
    }
    with patch(
        "src.backend.routers.metrics.metrics_service.get_dashboard",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.get(
            "/api/v1/metrics/dashboard?period_days=7",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["data"]["period_days"] == 7


@pytest.mark.asyncio
async def test_get_dashboard_invalid_period(client, auth_headers):
    """유효하지 않은 기간 시 422 반환."""
    resp = await client.get(
        "/api/v1/metrics/dashboard?period_days=0",
        headers=auth_headers,
    )

    assert resp.status_code == 422
