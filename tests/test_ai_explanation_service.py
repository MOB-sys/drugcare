"""AI 설명 서비스 단위 테스트."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.backend.schemas.interaction import InteractionResult
from src.backend.models.interaction import Severity


def _make_test_interaction(**overrides) -> InteractionResult:
    """테스트용 InteractionResult를 생성한다."""
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


# ---------------------------------------------------------------------------
# 캐시 히트
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_explanation_cache_hit():
    """캐시에 AI 설명이 있으면 OpenAI를 호출하지 않고 캐시 결과를 반환한다."""
    from src.backend.services.ai_explanation_service import generate_explanation

    cached = {"ai_explanation": "캐시된 설명", "ai_recommendation": "캐시된 대처"}
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps(cached)

    interaction = _make_test_interaction()
    result = await generate_explanation(mock_redis, interaction)

    assert result == cached


# ---------------------------------------------------------------------------
# OpenAI 호출 성공
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_explanation_openai_success():
    """캐시 미스 시 OpenAI를 호출하고 결과를 캐시에 저장한다."""
    from src.backend.services import ai_explanation_service

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        "이 두 약을 함께 먹으면 간에 부담이 될 수 있습니다. "
        "구체적인 사항은 의사/약사와 상담하세요.\n\n"
        "대처 방법: 복용 간격을 두고 드시는 것이 좋습니다."
    )

    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_response

    interaction = _make_test_interaction()

    with patch.object(ai_explanation_service, "_openai_client", mock_client):
        result = await ai_explanation_service.generate_explanation(mock_redis, interaction)

    assert result is not None
    assert "ai_explanation" in result
    assert "ai_recommendation" in result
    assert "의사/약사와 상담" in result["ai_explanation"]
    # 캐시에 저장됐는지 확인
    mock_redis.set.assert_called_once()


# ---------------------------------------------------------------------------
# API 키 미설정
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_openai_returns_none_without_api_key():
    """OpenAI 클라이언트가 None이면 _call_openai는 None을 반환한다."""
    from src.backend.services import ai_explanation_service

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    interaction = _make_test_interaction()

    with patch.object(ai_explanation_service, "_openai_client", None):
        result = await ai_explanation_service.generate_explanation(mock_redis, interaction)

    assert result is None


# ---------------------------------------------------------------------------
# OpenAI 에러 핸들링
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_call_openai_error_returns_none():
    """OpenAI 호출 실패 시 None을 반환한다 (기존 플로우 유지)."""
    from src.backend.services import ai_explanation_service

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_client = AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("API 에러")

    interaction = _make_test_interaction()

    with patch.object(ai_explanation_service, "_openai_client", mock_client):
        result = await ai_explanation_service.generate_explanation(mock_redis, interaction)

    assert result is None


# ---------------------------------------------------------------------------
# enhance_results
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_enhance_results_adds_ai_fields():
    """enhance_results는 각 결과에 AI 필드를 추가한다."""
    from src.backend.services import ai_explanation_service

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        "쉬운 설명입니다. 구체적인 사항은 의사/약사와 상담하세요.\n\n"
        "대처 방법: 간격을 두세요."
    )

    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_response

    interactions = [_make_test_interaction()]

    with patch.object(ai_explanation_service, "_openai_client", mock_client):
        results = await ai_explanation_service.enhance_results(mock_redis, interactions)

    assert len(results) == 1
    assert "ai_explanation" in results[0]
    assert results[0]["ai_explanation"] is not None


# ---------------------------------------------------------------------------
# 가드레일 검증
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_system_prompt_contains_guardrails():
    """시스템 프롬프트에 가드레일이 포함되어 있다."""
    from src.backend.services.ai_explanation_service import _SYSTEM_PROMPT

    assert "진단" in _SYSTEM_PROMPT
    assert "가능성" in _SYSTEM_PROMPT
    assert "의사/약사" in _SYSTEM_PROMPT
