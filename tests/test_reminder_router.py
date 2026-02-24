"""리마인더 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_create_reminder_success(client, auth_headers):
    """리마인더 생성 성공."""
    mock_result = {
        "id": 1,
        "device_id": "test",
        "cabinet_item_id": 1,
        "item_name": "타이레놀",
        "reminder_time": "09:00:00",
        "days_of_week": [0, 1, 2, 3, 4],
        "is_active": True,
        "memo": None,
        "created_at": "2025-01-01T00:00:00+00:00",
    }
    with patch(
        "src.backend.routers.reminders.reminder_service.create_reminder",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/reminders",
            json={
                "cabinet_item_id": 1,
                "reminder_time": "09:00:00",
                "days_of_week": [0, 1, 2, 3, 4],
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_create_reminder_cabinet_not_found(client, auth_headers):
    """존재하지 않는 복약함 아이템에 대한 리마인더 생성 시 404 반환."""
    with patch(
        "src.backend.routers.reminders.reminder_service.create_reminder",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            "/api/v1/reminders",
            json={
                "cabinet_item_id": 999,
                "reminder_time": "09:00:00",
                "days_of_week": [0],
            },
            headers=auth_headers,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_reminders(client, auth_headers):
    """리마인더 목록 조회 성공."""
    mock_items = [
        {
            "id": 1,
            "device_id": "test",
            "cabinet_item_id": 1,
            "item_name": "타이레놀",
            "reminder_time": "09:00:00",
            "days_of_week": [0, 1, 2, 3, 4],
            "is_active": True,
            "memo": None,
            "created_at": "2025-01-01T00:00:00+00:00",
        },
    ]
    with patch(
        "src.backend.routers.reminders.reminder_service.list_reminders",
        new_callable=AsyncMock,
        return_value=mock_items,
    ):
        resp = await client.get("/api/v1/reminders", headers=auth_headers)

    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_update_reminder_success(client, auth_headers):
    """리마인더 수정 성공."""
    mock_result = {
        "id": 1,
        "device_id": "test",
        "cabinet_item_id": 1,
        "item_name": "타이레놀",
        "reminder_time": "10:00:00",
        "days_of_week": [0, 1, 2, 3, 4],
        "is_active": True,
        "memo": "변경",
        "created_at": "2025-01-01T00:00:00+00:00",
    }
    with patch(
        "src.backend.routers.reminders.reminder_service.update_reminder",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.patch(
            "/api/v1/reminders/1",
            json={"reminder_time": "10:00:00", "memo": "변경"},
            headers=auth_headers,
        )

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_update_reminder_not_found(client, auth_headers):
    """존재하지 않는 리마인더 수정 시 404 반환."""
    with patch(
        "src.backend.routers.reminders.reminder_service.update_reminder",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.patch(
            "/api/v1/reminders/999",
            json={"memo": "test"},
            headers=auth_headers,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_reminder_not_found(client, auth_headers):
    """존재하지 않는 리마인더 삭제 시 404 반환."""
    with patch(
        "src.backend.routers.reminders.reminder_service.delete_reminder",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.delete(
            "/api/v1/reminders/999", headers=auth_headers
        )

    assert resp.status_code == 404
