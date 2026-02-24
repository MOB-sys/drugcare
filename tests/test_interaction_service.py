"""상호작용 서비스 단위 테스트."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import mock_interaction
from src.backend.services.interaction_service import check_interactions
from src.backend.schemas.interaction import InteractionItem, InteractionResult
from src.backend.models.interaction import ItemType, Severity


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _make_drug_item(item_id: int) -> InteractionItem:
    """테스트용 DRUG 타입 InteractionItem을 생성한다."""
    return InteractionItem(item_type=ItemType.DRUG, item_id=item_id)


def _make_supplement_item(item_id: int) -> InteractionItem:
    """테스트용 SUPPLEMENT 타입 InteractionItem을 생성한다."""
    return InteractionItem(item_type=ItemType.SUPPLEMENT, item_id=item_id)


def _make_interaction_result(**overrides) -> InteractionResult:
    """Pydantic model_validate 호환 InteractionResult 인스턴스를 생성한다.

    InteractionResult에 from_attributes 설정이 없으므로, MagicMock 대신
    실제 InteractionResult 인스턴스를 DB 결과로 사용한다.
    model_validate(InteractionResult_instance) 는 동일 인스턴스를 반환한다.
    """
    defaults = {
        "item_a_name": "타이레놀정500밀리그램",
        "item_b_name": "아스피린정",
        "severity": Severity.WARNING,
        "description": "간독성 위험 증가",
        "mechanism": "아세트아미노펜과 아스피린의 간 대사 경쟁",
        "recommendation": "동시 복용 자제 권고",
        "source": "DUR",
        "evidence_level": "official",
    }
    defaults.update(overrides)
    return InteractionResult(**defaults)


def _mock_db_with_interactions(interactions: list) -> AsyncMock:
    """주어진 상호작용 목록을 반환하는 mock DB를 생성한다."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = interactions
    mock_db.execute = AsyncMock(return_value=mock_result)
    return mock_db


# ---------------------------------------------------------------------------
# check_interactions — 기본 동작
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_two_drugs_no_interaction():
    """2개 약물 간 상호작용이 없으면 interactions_found=0, has_danger=False를 반환한다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["interactions_found"] == 0
    assert result["has_danger"] is False
    assert result["total_checked"] == 1


@pytest.mark.asyncio
async def test_check_two_drugs_with_interaction():
    """2개 약물 간 상호작용이 있으면 interactions_found=1을 반환한다."""
    interaction = _make_interaction_result()
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["interactions_found"] == 1
    assert result["total_checked"] == 1


@pytest.mark.asyncio
async def test_check_drug_supplement_cross():
    """약물+영양제 교차 쌍 상호작용이 올바르게 감지된다."""
    interaction = _make_interaction_result(
        item_b_name="비타민C",
    )
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_supplement_item(10)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["interactions_found"] == 1
    assert result["total_checked"] == 1


# ---------------------------------------------------------------------------
# check_interactions — nC2 조합 수
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_three_items_nc2():
    """3개 아이템은 3C2=3개 쌍을 체크한다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2), _make_drug_item(3)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["total_checked"] == 3


@pytest.mark.asyncio
async def test_check_four_items_nc2():
    """4개 아이템은 4C2=6개 쌍을 체크한다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [
        _make_drug_item(1),
        _make_drug_item(2),
        _make_supplement_item(3),
        _make_supplement_item(4),
    ]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["total_checked"] == 6


# ---------------------------------------------------------------------------
# check_interactions — 심각도 판정 및 정렬
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_has_danger_true():
    """DANGER 심각도 상호작용이 있으면 has_danger=True를 반환한다."""
    interaction = _make_interaction_result(severity=Severity.DANGER)
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["has_danger"] is True


@pytest.mark.asyncio
async def test_check_has_danger_false():
    """WARNING 이하 심각도만 있으면 has_danger=False를 반환한다."""
    interaction = _make_interaction_result(severity=Severity.WARNING)
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["has_danger"] is False


@pytest.mark.asyncio
async def test_check_severity_sorting():
    """결과는 심각도 순(DANGER 우선)으로 정렬된다."""
    info_interaction = _make_interaction_result(
        severity=Severity.INFO,
        item_a_name="약A",
        item_b_name="약B",
        description="정보 제공",
    )
    danger_interaction = _make_interaction_result(
        severity=Severity.DANGER,
        item_a_name="약C",
        item_b_name="약D",
        description="병용금기",
    )
    mock_db = _mock_db_with_interactions([info_interaction, danger_interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert len(result["results"]) == 2
    assert result["results"][0]["severity"] == Severity.DANGER
    assert result["results"][1]["severity"] == Severity.INFO


# ---------------------------------------------------------------------------
# check_interactions — 캐시
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_cache_hit():
    """캐시 히트 시 DB를 호출하지 않고 캐시된 결과를 반환한다."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()

    cached_data = {
        "total_checked": 1,
        "interactions_found": 1,
        "has_danger": False,
        "results": [],
        "disclaimer": "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.",
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result == cached_data
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_check_cache_miss_stores():
    """캐시 미스 시 DB 조회 후 결과를 Redis에 저장한다."""
    mock_db = _mock_db_with_interactions([_make_interaction_result()])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["interactions_found"] == 1
    mock_redis.set.assert_called_once()


# ---------------------------------------------------------------------------
# check_interactions — 면책조항 및 캐시 키 순서 독립성
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_disclaimer_present():
    """응답에 면책조항(disclaimer) 필드가 포함된다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert "disclaimer" in result
    assert "의사/약사" in result["disclaimer"]


@pytest.mark.asyncio
async def test_check_order_independent_cache_key():
    """아이템 순서를 바꿔도 동일한 캐시 결과를 사용한다 (순서 무관 캐시 키)."""
    cached_data = {
        "total_checked": 1,
        "interactions_found": 0,
        "has_danger": False,
        "results": [],
        "disclaimer": "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다.",
    }

    # 순서 [A, B]로 호출
    mock_db_1 = AsyncMock()
    mock_redis_1 = AsyncMock()
    mock_redis_1.get.return_value = json.dumps(cached_data)

    items_ab = [_make_drug_item(1), _make_drug_item(2)]
    result_ab = await check_interactions(mock_db_1, mock_redis_1, items_ab)

    # 순서 [B, A]로 호출
    mock_db_2 = AsyncMock()
    mock_redis_2 = AsyncMock()
    mock_redis_2.get.return_value = json.dumps(cached_data)

    items_ba = [_make_drug_item(2), _make_drug_item(1)]
    result_ba = await check_interactions(mock_db_2, mock_redis_2, items_ba)

    # 두 호출 모두 캐시 히트이므로 DB 미호출
    mock_db_1.execute.assert_not_called()
    mock_db_2.execute.assert_not_called()

    # redis.get에 전달된 캐시 키가 동일해야 한다
    key_ab = mock_redis_1.get.call_args[0][0]
    key_ba = mock_redis_2.get.call_args[0][0]
    assert key_ab == key_ba

    assert result_ab == result_ba
