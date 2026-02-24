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


# ---------------------------------------------------------------------------
# check_interactions — AI 설명 통합
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_interactions_with_ai_key():
    """OPENAI_API_KEY가 설정되면 결과에 AI 필드가 포함된다."""
    interaction = _make_interaction_result()
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]

    with patch("src.backend.services.interaction_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = "test-key"
        with patch(
            "src.backend.services.ai_explanation_service.enhance_results",
            new_callable=AsyncMock,
        ) as mock_enhance:
            mock_enhance.return_value = [
                {
                    "item_a_name": "타이레놀정500밀리그램",
                    "item_b_name": "아스피린정",
                    "severity": "warning",
                    "ai_explanation": "AI 설명",
                    "ai_recommendation": "AI 대처",
                },
            ]
            result = await check_interactions(mock_db, mock_redis, items)

    assert result["results"][0]["ai_explanation"] == "AI 설명"


@pytest.mark.asyncio
async def test_check_interactions_without_ai_key():
    """OPENAI_API_KEY가 비어있으면 기존 동작을 유지한다."""
    interaction = _make_interaction_result()
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]

    with patch("src.backend.services.interaction_service.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        result = await check_interactions(mock_db, mock_redis, items)

    # AI 필드는 없거나 None
    first_result = result["results"][0]
    assert first_result.get("ai_explanation") is None


# ---------------------------------------------------------------------------
# check_interactions — 엣지 케이스
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_single_item_no_pairs():
    """아이템이 1개이면 조합이 불가하므로 total_checked=0을 반환한다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["total_checked"] == 0
    assert result["interactions_found"] == 0
    assert result["has_danger"] is False


@pytest.mark.asyncio
async def test_check_ten_items_45_pairs():
    """10개 아이템은 10C2=45개 쌍을 체크한다."""
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(i) for i in range(1, 11)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["total_checked"] == 45


@pytest.mark.asyncio
async def test_check_duplicate_items_no_self_interaction():
    """동일 아이템이 중복되어도 자기 자신과의 상호작용은 쌍으로 생성된다.

    combinations는 인덱스 기반이므로 동일 item_id 쌍이 생기지만,
    DB에 자기 자신과의 상호작용 레코드가 없으면 결과는 0건이다.
    """
    mock_db = _mock_db_with_interactions([])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(1)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["total_checked"] == 1
    assert result["interactions_found"] == 0


@pytest.mark.asyncio
async def test_check_cache_set_failure_still_returns_result():
    """cache_set 실패 시에도 정상 결과를 반환한다 (graceful degradation)."""
    interaction = _make_interaction_result()
    mock_db = _mock_db_with_interactions([interaction])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.side_effect = ConnectionError("Redis down")

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    assert result["interactions_found"] == 1
    assert result["total_checked"] == 1


@pytest.mark.asyncio
async def test_check_mixed_severity_sorting_all_four():
    """4가지 심각도(DANGER, WARNING, CAUTION, INFO)가 모두 포함될 때 올바르게 정렬된다."""
    danger = _make_interaction_result(
        severity=Severity.DANGER,
        item_a_name="약A", item_b_name="약B",
        description="병용금기",
    )
    warning = _make_interaction_result(
        severity=Severity.WARNING,
        item_a_name="약C", item_b_name="약D",
        description="주의",
    )
    caution = _make_interaction_result(
        severity=Severity.CAUTION,
        item_a_name="약E", item_b_name="약F",
        description="경고",
    )
    info = _make_interaction_result(
        severity=Severity.INFO,
        item_a_name="약G", item_b_name="약H",
        description="정보",
    )
    # 역순으로 넣어서 정렬 검증
    mock_db = _mock_db_with_interactions([info, caution, warning, danger])
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    items = [_make_drug_item(1), _make_drug_item(2)]
    result = await check_interactions(mock_db, mock_redis, items)

    severities = [r["severity"] for r in result["results"]]
    assert severities == [
        Severity.DANGER,
        Severity.WARNING,
        Severity.CAUTION,
        Severity.INFO,
    ]
    assert result["has_danger"] is True
