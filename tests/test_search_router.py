"""통합 검색 라우터 테스트."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_search_suggest_success(client, auth_headers):
    """통합 자동완성 성공 시 4종 타입 결과를 합쳐서 반환한다."""
    mock_drugs = [{"name": "타이레놀", "slug": "drug-1", "type": "drug"}]
    mock_supps = [{"name": "비타민C", "slug": "supp-1", "type": "supplement"}]
    mock_foods = [{"name": "자몽", "slug": "food-1", "type": "food"}]
    mock_herbals = [{"name": "인삼", "slug": "herbal-1", "type": "herbal"}]

    with (
        patch(
            "src.backend.routers.search.drug_service.suggest_drugs",
            new_callable=AsyncMock,
            return_value=mock_drugs,
        ),
        patch(
            "src.backend.routers.search.supplement_service.suggest_supplements",
            new_callable=AsyncMock,
            return_value=mock_supps,
        ),
        patch(
            "src.backend.routers.search.food_service.suggest_foods",
            new_callable=AsyncMock,
            return_value=mock_foods,
        ),
        patch(
            "src.backend.routers.search.herbal_medicine_service.suggest_herbal_medicines",
            new_callable=AsyncMock,
            return_value=mock_herbals,
        ),
    ):
        resp = await client.get(
            "/api/v1/search/suggest?q=타이레놀", headers=auth_headers
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 4
    types = {item["type"] for item in body["data"]}
    assert types == {"drug", "supplement", "food", "herbal"}


@pytest.mark.asyncio
async def test_search_suggest_respects_limit(client, auth_headers):
    """limit 파라미터로 결과 수를 제한한다."""
    mock_items = [{"name": f"약물{i}", "slug": f"drug-{i}", "type": "drug"} for i in range(5)]

    with (
        patch(
            "src.backend.routers.search.drug_service.suggest_drugs",
            new_callable=AsyncMock,
            return_value=mock_items,
        ),
        patch(
            "src.backend.routers.search.supplement_service.suggest_supplements",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "src.backend.routers.search.food_service.suggest_foods",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "src.backend.routers.search.herbal_medicine_service.suggest_herbal_medicines",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        resp = await client.get(
            "/api/v1/search/suggest?q=약물&limit=3", headers=auth_headers
        )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 3


@pytest.mark.asyncio
async def test_search_suggest_short_query(client, auth_headers):
    """2자 미만 검색어는 422 에러를 반환한다."""
    resp = await client.get(
        "/api/v1/search/suggest?q=타", headers=auth_headers
    )
    assert resp.status_code == 422
