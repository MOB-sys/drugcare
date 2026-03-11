"""의약품 서비스 단위 테스트."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import mock_drug
from src.backend.services.drug_service import search_drugs, get_drug_detail


# ---------------------------------------------------------------------------
# search_drugs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_drugs_empty_query():
    """빈 검색어는 전체 목록을 반환한다 (조건 없이 DB 조회)."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_drugs(mock_db, mock_redis, q="", page=1, page_size=20)

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


@pytest.mark.asyncio
async def test_search_drugs_with_results():
    """검색어 매칭 시 아이템 목록, total, total_pages를 올바르게 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    drug1 = mock_drug()
    drug2 = mock_drug(id=2, item_name="타이레놀이알정", item_seq="200005678")

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 2

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = [drug1, drug2]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_drugs(mock_db, mock_redis, q="타이레놀", page=1, page_size=20)

    assert len(result["items"]) == 2
    assert result["total"] == 2
    assert result["total_pages"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 20


@pytest.mark.asyncio
async def test_search_drugs_no_results():
    """매칭 결과가 없으면 빈 아이템 목록과 total=0을 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_drugs(mock_db, mock_redis, q="존재하지않는약", page=1, page_size=20)

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


@pytest.mark.asyncio
async def test_search_drugs_cache_hit():
    """캐시 히트 시 DB를 호출하지 않고 캐시된 결과를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()

    cached_data = {
        "items": [{"id": 1, "item_seq": "200001234", "item_name": "타이레놀정500밀리그램"}],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    result = await search_drugs(mock_db, mock_redis, q="타이레놀", page=1, page_size=20)

    assert result == cached_data
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_search_drugs_cache_miss_stores():
    """캐시 미스 시 DB 조회 후 결과를 Redis에 저장한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    drug1 = mock_drug()

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = [drug1]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_drugs(mock_db, mock_redis, q="타이레놀", page=1, page_size=20)

    assert len(result["items"]) == 1
    mock_redis.set.assert_called_once()


# ---------------------------------------------------------------------------
# get_drug_detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_drug_detail_found():
    """존재하는 의약품 ID 조회 시 상세 정보 dict를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    drug = mock_drug()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = drug
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_drug_detail(mock_db, mock_redis, drug_id=1)

    assert result is not None
    assert result["id"] == 1
    assert result["item_name"] == "타이레놀정500밀리그램"
    assert result["entp_name"] == "한국얀센"
    assert result["material_name"] == "아세트아미노펜"


@pytest.mark.asyncio
async def test_get_drug_detail_not_found():
    """존재하지 않는 의약품 ID 조회 시 None을 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_drug_detail(mock_db, mock_redis, drug_id=9999)

    assert result is None
