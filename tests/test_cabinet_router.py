"""복약함 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_add_cabinet_item_success(client, auth_headers):
    """복약함 아이템 추가 성공."""
    mock_result = {
        "id": 1,
        "device_id": "test-device",
        "item_type": "drug",
        "item_id": 1,
        "item_name": "타이레놀",
        "nickname": None,
        "created_at": "2025-01-01T00:00:00+00:00",
    }
    with patch(
        "src.backend.routers.cabinet.cabinet_service.add_item",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/cabinet",
            json={"item_type": "drug", "item_id": 1},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_add_cabinet_item_not_found(client, auth_headers):
    """존재하지 않는 약물/영양제 추가 시 404 반환."""
    with patch(
        "src.backend.routers.cabinet.cabinet_service.add_item",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            "/api/v1/cabinet",
            json={"item_type": "drug", "item_id": 99999},
            headers=auth_headers,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_cabinet_item_duplicate(client, auth_headers):
    """이미 등록된 아이템 추가 시 409 Conflict 반환."""
    with patch(
        "src.backend.routers.cabinet.cabinet_service.add_item",
        new_callable=AsyncMock,
        return_value="duplicate",
    ):
        resp = await client.post(
            "/api/v1/cabinet",
            json={"item_type": "drug", "item_id": 1},
            headers=auth_headers,
        )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_cabinet_items(client, auth_headers):
    """복약함 목록 조회 성공."""
    mock_items = [
        {
            "id": 1,
            "device_id": "test",
            "item_type": "drug",
            "item_id": 1,
            "item_name": "타이레놀",
            "nickname": None,
            "created_at": "2025-01-01T00:00:00+00:00",
        },
    ]
    with patch(
        "src.backend.routers.cabinet.cabinet_service.list_items",
        new_callable=AsyncMock,
        return_value=mock_items,
    ):
        resp = await client.get("/api/v1/cabinet", headers=auth_headers)

    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_delete_cabinet_item_success(client, auth_headers):
    """복약함 아이템 삭제 성공."""
    with patch(
        "src.backend.routers.cabinet.cabinet_service.delete_item",
        new_callable=AsyncMock,
        return_value=True,
    ):
        resp = await client.delete("/api/v1/cabinet/1", headers=auth_headers)

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_cabinet_item_not_found(client, auth_headers):
    """존재하지 않는 복약함 아이템 삭제 시 404 반환."""
    with patch(
        "src.backend.routers.cabinet.cabinet_service.delete_item",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.delete(
            "/api/v1/cabinet/99999", headers=auth_headers
        )

    assert resp.status_code == 404
