"""자동완성(suggest) 서비스 단위 테스트 — 4종 타입."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.backend.services.drug_service import suggest_drugs
from src.backend.services.food_service import suggest_foods
from src.backend.services.herbal_medicine_service import suggest_herbal_medicines
from src.backend.services.supplement_service import suggest_supplements


def _mock_db_with_rows(rows: list[tuple]) -> AsyncMock:
    """suggest 쿼리용 mock DB 세션을 생성한다."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = rows
    mock_db.execute.return_value = mock_result
    return mock_db


def _mock_redis_no_cache() -> AsyncMock:
    """캐시 미스 상태의 mock Redis를 생성한다."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    return mock_redis


# ---------------------------------------------------------------------------
# suggest_drugs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_drugs_returns_results():
    """검색어 매칭 시 drug 타입 제안 목록을 반환한다."""
    rows = [("타이레놀정500밀리그램", "drug-200001234"), ("타이레놀이알정", "drug-200005678")]
    mock_db = _mock_db_with_rows(rows)
    mock_redis = _mock_redis_no_cache()

    result = await suggest_drugs(mock_db, mock_redis, "타이레놀", 10)

    assert len(result) == 2
    assert result[0] == {"name": "타이레놀정500밀리그램", "slug": "drug-200001234", "type": "drug"}
    assert result[1]["type"] == "drug"


@pytest.mark.asyncio
async def test_suggest_drugs_short_query_returns_empty():
    """2자 미만 검색어는 빈 리스트를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()

    result = await suggest_drugs(mock_db, mock_redis, "타", 10)

    assert result == []
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_suggest_drugs_cache_hit():
    """캐시 히트 시 DB 조회 없이 캐시 결과를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    cached = [{"name": "캐시결과", "slug": "drug-1", "type": "drug"}]
    mock_redis.get.return_value = '{"v": ' + __import__("json").dumps(cached) + "}"

    # cache_get은 redis.get을 호출하므로 직접 패치
    from unittest.mock import patch

    with patch("src.backend.services.drug_service.cache_get", return_value=cached):
        result = await suggest_drugs(mock_db, mock_redis, "캐시", 10)

    assert result == cached
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_suggest_drugs_empty_results():
    """매칭 결과가 없으면 빈 리스트를 반환한다."""
    mock_db = _mock_db_with_rows([])
    mock_redis = _mock_redis_no_cache()

    result = await suggest_drugs(mock_db, mock_redis, "존재하지않는약", 10)

    assert result == []


# ---------------------------------------------------------------------------
# suggest_supplements
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_supplements_returns_results():
    """영양제 제안 목록을 반환한다."""
    rows = [("종근당 비타민C", "supp-1")]
    mock_db = _mock_db_with_rows(rows)
    mock_redis = _mock_redis_no_cache()

    result = await suggest_supplements(mock_db, mock_redis, "비타민", 10)

    assert len(result) == 1
    assert result[0]["type"] == "supplement"
    assert result[0]["name"] == "종근당 비타민C"


@pytest.mark.asyncio
async def test_suggest_supplements_short_query():
    """2자 미만 검색어는 빈 리스트를 반환한다."""
    result = await suggest_supplements(AsyncMock(), AsyncMock(), "비", 10)
    assert result == []


# ---------------------------------------------------------------------------
# suggest_foods
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_foods_returns_results():
    """식품 제안 목록을 반환한다."""
    rows = [("자몽", "food-grapefruit")]
    mock_db = _mock_db_with_rows(rows)
    mock_redis = _mock_redis_no_cache()

    result = await suggest_foods(mock_db, mock_redis, "자몽", 10)

    assert len(result) == 1
    assert result[0]["type"] == "food"


@pytest.mark.asyncio
async def test_suggest_foods_short_query():
    """2자 미만 검색어는 빈 리스트를 반환한다."""
    result = await suggest_foods(AsyncMock(), AsyncMock(), "자", 10)
    assert result == []


# ---------------------------------------------------------------------------
# suggest_herbal_medicines
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggest_herbals_returns_results():
    """한약재 제안 목록을 반환한다."""
    rows = [("인삼", "herbal-ginseng")]
    mock_db = _mock_db_with_rows(rows)
    mock_redis = _mock_redis_no_cache()

    result = await suggest_herbal_medicines(mock_db, mock_redis, "인삼", 10)

    assert len(result) == 1
    assert result[0]["type"] == "herbal"


@pytest.mark.asyncio
async def test_suggest_herbals_short_query():
    """2자 미만 검색어는 빈 리스트를 반환한다."""
    result = await suggest_herbal_medicines(AsyncMock(), AsyncMock(), "인", 10)
    assert result == []
