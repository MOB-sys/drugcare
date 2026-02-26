"""의약품 slug API 테스트 — slugs, count, by-slug 엔드포인트."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from tests.conftest import mock_drug


@pytest.mark.asyncio
async def test_get_drug_slugs_success(client, auth_headers):
    """GET /drugs/slugs — slug 목록 반환."""
    slugs = ["drug-200001234", "drug-200005678"]
    with patch(
        "src.backend.services.drug_service.get_all_drug_slugs",
        new_callable=AsyncMock,
        return_value=slugs,
    ):
        resp = await client.get("/api/v1/drugs/slugs", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == slugs


@pytest.mark.asyncio
async def test_get_drug_slugs_no_auth_required(client):
    """GET /drugs/slugs — 인증 없이 접근 가능 (EXEMPT_PREFIXES)."""
    slugs = ["drug-200001234"]
    with patch(
        "src.backend.services.drug_service.get_all_drug_slugs",
        new_callable=AsyncMock,
        return_value=slugs,
    ):
        resp = await client.get("/api/v1/drugs/slugs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_drug_count_success(client, auth_headers):
    """GET /drugs/count — 총 건수 반환."""
    with patch(
        "src.backend.services.drug_service.count_drugs",
        new_callable=AsyncMock,
        return_value=12345,
    ):
        resp = await client.get("/api/v1/drugs/count", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == 12345


@pytest.mark.asyncio
async def test_get_drug_count_no_auth_required(client):
    """GET /drugs/count — 인증 없이 접근 가능."""
    with patch(
        "src.backend.services.drug_service.count_drugs",
        new_callable=AsyncMock,
        return_value=100,
    ):
        resp = await client.get("/api/v1/drugs/count")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_drug_by_slug_success(client, auth_headers):
    """GET /drugs/by-slug/{slug} — 성공 조회."""
    drug = mock_drug()
    detail = {
        "id": drug.id,
        "item_seq": drug.item_seq,
        "item_name": drug.item_name,
        "slug": drug.slug,
        "entp_name": drug.entp_name,
        "etc_otc_code": drug.etc_otc_code,
        "class_no": drug.class_no,
        "chart": drug.chart,
        "bar_code": drug.bar_code,
        "material_name": drug.material_name,
        "ingredients": drug.ingredients,
        "efcy_qesitm": drug.efcy_qesitm,
        "use_method_qesitm": drug.use_method_qesitm,
        "atpn_warn_qesitm": drug.atpn_warn_qesitm,
        "atpn_qesitm": drug.atpn_qesitm,
        "intrc_qesitm": drug.intrc_qesitm,
        "se_qesitm": drug.se_qesitm,
        "deposit_method_qesitm": drug.deposit_method_qesitm,
        "item_image": drug.item_image,
    }
    with patch(
        "src.backend.services.drug_service.get_drug_by_slug",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/v1/drugs/by-slug/drug-200001234", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["slug"] == "drug-200001234"


@pytest.mark.asyncio
async def test_get_drug_by_slug_not_found(client, auth_headers):
    """GET /drugs/by-slug/{slug} — 존재하지 않는 slug 404."""
    with patch(
        "src.backend.services.drug_service.get_drug_by_slug",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.get("/api/v1/drugs/by-slug/drug-nonexistent", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_drug_by_slug_no_auth_required(client):
    """GET /drugs/by-slug/{slug} — 인증 없이 접근 가능."""
    detail = {"id": 1, "item_seq": "200001234", "item_name": "테스트", "slug": "drug-200001234"}
    with patch(
        "src.backend.services.drug_service.get_drug_by_slug",
        new_callable=AsyncMock,
        return_value=detail,
    ):
        resp = await client.get("/api/v1/drugs/by-slug/drug-200001234")
    assert resp.status_code == 200
