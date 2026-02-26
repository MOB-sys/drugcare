"""영양제 slug API 테스트 — slugs, count, by-slug 엔드포인트."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import mock_supplement


@pytest.mark.asyncio
async def test_get_supplement_slugs_success(client, auth_headers):
    """GET /supplements/slugs — slug 목록 반환."""
    slugs = ["supp-1", "supp-2", "supp-3"]
    with patch(
        "src.backend.services.supplement_service.get_all_supplement_slugs",
        new_callable=AsyncMock,
        return_value=slugs,
    ):
        resp = await client.get("/api/v1/supplements/slugs", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == slugs


@pytest.mark.asyncio
async def test_get_supplement_slugs_no_auth_required(client):
    """GET /supplements/slugs — 인증 없이 접근 가능 (EXEMPT_PREFIXES)."""
    with patch(
        "src.backend.services.supplement_service.get_all_supplement_slugs",
        new_callable=AsyncMock,
        return_value=["supp-1"],
    ):
        resp = await client.get("/api/v1/supplements/slugs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_supplement_count_success(client, auth_headers):
    """GET /supplements/count — 총 건수 반환."""
    with patch(
        "src.backend.services.supplement_service.count_supplements",
        new_callable=AsyncMock,
        return_value=567,
    ):
        resp = await client.get("/api/v1/supplements/count", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == 567


@pytest.mark.asyncio
async def test_get_supplement_count_no_auth_required(client):
    """GET /supplements/count — 인증 없이 접근 가능."""
    with patch(
        "src.backend.services.supplement_service.count_supplements",
        new_callable=AsyncMock,
        return_value=100,
    ):
        resp = await client.get("/api/v1/supplements/count")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_supplement_by_slug_success(client, auth_headers):
    """GET /supplements/by-slug/{slug} — 성공 조회."""
    supp = mock_supplement()
    detail = {
        "id": supp.id,
        "product_name": supp.product_name,
        "slug": supp.slug,
        "company": supp.company,
        "registration_no": supp.registration_no,
        "main_ingredient": supp.main_ingredient,
        "ingredients": supp.ingredients,
        "functionality": supp.functionality,
        "precautions": supp.precautions,
        "intake_method": supp.intake_method,
        "category": supp.category,
        "source": supp.source,
    }
    with patch(
        "src.backend.services.supplement_service.get_supplement_by_slug",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/v1/supplements/by-slug/supp-1", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["slug"] == "supp-1"


@pytest.mark.asyncio
async def test_get_supplement_by_slug_not_found(client, auth_headers):
    """GET /supplements/by-slug/{slug} — 존재하지 않는 slug 404."""
    with patch(
        "src.backend.services.supplement_service.get_supplement_by_slug",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.get("/api/v1/supplements/by-slug/supp-nonexistent", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_supplement_by_slug_no_auth_required(client):
    """GET /supplements/by-slug/{slug} — 인증 없이 접근 가능."""
    detail = {"id": 1, "product_name": "테스트", "slug": "supp-1"}
    with patch(
        "src.backend.services.supplement_service.get_supplement_by_slug",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/v1/supplements/by-slug/supp-1")
    assert resp.status_code == 200
