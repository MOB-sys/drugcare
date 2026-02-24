"""영양제 라우터 통합 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_search_supplements_success(client, auth_headers):
    """검색 성공 시 ApiResponse 포맷 반환."""
    mock_result = {
        "items": [
            {
                "id": 1,
                "product_name": "종근당 비타민C 1000",
                "company": "종근당건강",
                "main_ingredient": "비타민C",
                "category": "비타민",
            },
        ],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }
    with patch(
        "src.backend.routers.supplements.supplement_service.search_supplements",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.get(
            "/api/v1/supplements/search?q=비타민", headers=auth_headers
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_search_supplements_empty_query(client, auth_headers):
    """빈 검색어 시 빈 결과 반환."""
    mock_result = {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "total_pages": 0,
    }
    with patch(
        "src.backend.routers.supplements.supplement_service.search_supplements",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.get(
            "/api/v1/supplements/search?q=", headers=auth_headers
        )

    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


@pytest.mark.asyncio
async def test_get_supplement_detail_found(client, auth_headers):
    """상세 조회 성공."""
    mock_detail = {
        "id": 1,
        "product_name": "종근당 비타민C 1000",
        "company": "종근당건강",
        "main_ingredient": "비타민C",
        "category": "비타민",
    }
    with patch(
        "src.backend.routers.supplements.supplement_service.get_supplement_detail",
        new_callable=AsyncMock,
        return_value=mock_detail,
    ):
        resp = await client.get(
            "/api/v1/supplements/1", headers=auth_headers
        )

    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_get_supplement_detail_not_found(client, auth_headers):
    """존재하지 않는 영양제 조회 시 404 반환."""
    with patch(
        "src.backend.routers.supplements.supplement_service.get_supplement_detail",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.get(
            "/api/v1/supplements/99999", headers=auth_headers
        )

    assert resp.status_code == 404
    assert resp.json()["success"] is False


@pytest.mark.asyncio
async def test_search_supplements_invalid_page(client, auth_headers):
    """잘못된 page 파라미터(0 이하) 전달 시 422 Validation Error 반환."""
    resp = await client.get(
        "/api/v1/supplements/search?q=test&page=0", headers=auth_headers
    )

    assert resp.status_code == 422
