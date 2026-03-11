"""영양제 서비스 단위 테스트."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import mock_supplement
from src.backend.services.supplement_service import search_supplements, get_supplement_detail


# ---------------------------------------------------------------------------
# search_supplements
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_supplements_empty_query():
    """빈 검색어는 전체 목록을 반환한다 (조건 없이 DB 조회)."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_supplements(mock_db, mock_redis, q="", page=1, page_size=20)

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


@pytest.mark.asyncio
async def test_search_supplements_with_results():
    """검색어 매칭 시 아이템 목록, total, total_pages를 올바르게 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    supp1 = mock_supplement()
    supp2 = mock_supplement(id=2, product_name="종근당 아연", registration_no="20040020099999")

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 2

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = [supp1, supp2]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_supplements(mock_db, mock_redis, q="종근당", page=1, page_size=20)

    assert len(result["items"]) == 2
    assert result["total"] == 2
    assert result["total_pages"] == 1
    assert result["page"] == 1
    assert result["page_size"] == 20


@pytest.mark.asyncio
async def test_search_supplements_no_results():
    """매칭 결과가 없으면 빈 아이템 목록과 total=0을 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_supplements(mock_db, mock_redis, q="존재하지않는영양제", page=1, page_size=20)

    assert result["items"] == []
    assert result["total"] == 0
    assert result["total_pages"] == 0


@pytest.mark.asyncio
async def test_search_supplements_cache_hit():
    """캐시 히트 시 DB를 호출하지 않고 캐시된 결과를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()

    cached_data = {
        "items": [{"id": 1, "product_name": "종근당 비타민C 1000", "company": "종근당건강"}],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    result = await search_supplements(mock_db, mock_redis, q="비타민", page=1, page_size=20)

    assert result == cached_data
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_search_supplements_cache_miss_stores():
    """캐시 미스 시 DB 조회 후 결과를 Redis에 저장한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    supp1 = mock_supplement()

    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1

    mock_search_result = MagicMock()
    mock_search_result.scalars.return_value.all.return_value = [supp1]

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_search_result])

    result = await search_supplements(mock_db, mock_redis, q="비타민", page=1, page_size=20)

    assert len(result["items"]) == 1
    mock_redis.set.assert_called_once()


# ---------------------------------------------------------------------------
# get_supplement_detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_supplement_detail_found():
    """존재하는 영양제 ID 조회 시 상세 정보 dict를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    supp = mock_supplement()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = supp
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_supplement_detail(mock_db, mock_redis, supplement_id=1)

    assert result is not None
    assert result["id"] == 1
    assert result["product_name"] == "종근당 비타민C 1000"
    assert result["company"] == "종근당건강"
    assert result["functionality"] == "항산화 작용"


@pytest.mark.asyncio
async def test_get_supplement_detail_not_found():
    """존재하지 않는 영양제 ID 조회 시 None을 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_supplement_detail(mock_db, mock_redis, supplement_id=9999)

    assert result is None
