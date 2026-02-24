"""AI 설명 생성 서비스 — GPT-4o 기반 상호작용 쉬운 설명."""

import asyncio
import logging

from openai import AsyncOpenAI
from redis.asyncio import Redis

from src.backend.core.config import get_settings
from src.backend.core.redis import CACHE_TTL_AI_EXPLANATION
from src.backend.schemas.interaction import InteractionResult
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

logger = logging.getLogger(__name__)

settings = get_settings()

# OpenAI 클라이언트 — API 키가 있을 때만 초기화
_openai_client: AsyncOpenAI | None = None
if settings.OPENAI_API_KEY:
    _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# 병렬 호출 제한
_SEMAPHORE = asyncio.Semaphore(3)

_SYSTEM_PROMPT = """당신은 약물 상호작용 정보를 일반인이 이해하기 쉽게 설명하는 전문가입니다.

규칙:
1. 쉬운 한국어로 3~4문장으로 설명하세요.
2. 의학적 진단이나 치료를 제안하지 마세요.
3. "~할 수 있습니다", "~가능성이 있습니다" 등 가능성 표현을 사용하세요.
4. 마지막에 반드시 "구체적인 사항은 의사/약사와 상담하세요."로 마무리하세요.
5. 약 이름은 그대로 사용하세요.
"""


async def generate_explanation(
    redis: Redis,
    interaction: InteractionResult,
) -> dict | None:
    """단일 상호작용에 대한 AI 설명을 생성한다.

    Redis 캐시를 먼저 확인하고, 캐시 미스 시 OpenAI를 호출한다.

    Args:
        redis: Redis 클라이언트.
        interaction: 설명할 상호작용 결과.

    Returns:
        {"ai_explanation": str, "ai_recommendation": str} 또는 None.
    """
    cache_key = make_cache_key(
        "ai",
        "explanation",
        hash_query(f"{interaction.item_a_name}:{interaction.item_b_name}:{interaction.severity}"),
    )

    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    result = await _call_openai(interaction)
    if result is not None:
        await cache_set(redis, cache_key, result, CACHE_TTL_AI_EXPLANATION)

    return result


async def _call_openai(interaction: InteractionResult) -> dict | None:
    """OpenAI GPT-4o를 호출하여 쉬운 설명을 생성한다.

    API 키가 없거나 에러 발생 시 None을 반환한다.

    Args:
        interaction: 설명할 상호작용 결과.

    Returns:
        {"ai_explanation": str, "ai_recommendation": str} 또는 None.
    """
    if _openai_client is None:
        return None

    user_prompt = (
        f"약물A: {interaction.item_a_name}\n"
        f"약물B: {interaction.item_b_name}\n"
        f"심각도: {interaction.severity}\n"
        f"설명: {interaction.description or '없음'}\n"
        f"기전: {interaction.mechanism or '없음'}\n\n"
        "위 상호작용을 일반인이 이해하기 쉽게 설명해주세요.\n"
        "그리고 줄바꿈 후 '대처 방법:'으로 시작하는 실용적인 대처 방법을 1~2문장으로 알려주세요."
    )

    try:
        async with _SEMAPHORE:
            response = await _openai_client.chat.completions.create(
                model="gpt-4o",
                temperature=0.3,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )

        content = response.choices[0].message.content or ""

        # "대처 방법:" 구분자로 분리
        if "대처 방법:" in content:
            parts = content.split("대처 방법:", 1)
            explanation = parts[0].strip()
            recommendation = parts[1].strip()
        else:
            explanation = content.strip()
            recommendation = None

        return {
            "ai_explanation": explanation,
            "ai_recommendation": recommendation,
        }
    except Exception:
        logger.warning("OpenAI 호출 실패", exc_info=True)
        return None


async def enhance_results(
    redis: Redis,
    results: list[InteractionResult],
) -> list[dict]:
    """상호작용 결과 목록에 AI 설명을 추가한다.

    description 또는 mechanism이 None인 결과를 우선으로 AI 설명을 생성한다.

    Args:
        redis: Redis 클라이언트.
        results: 상호작용 결과 목록.

    Returns:
        AI 설명이 추가된 dict 목록.
    """

    async def _enhance_single(result: InteractionResult) -> dict:
        """단일 결과에 AI 설명을 추가한다."""
        result_dict = result.model_dump() if hasattr(result, "model_dump") else dict(result)
        ai_data = await generate_explanation(redis, result)
        if ai_data:
            result_dict["ai_explanation"] = ai_data.get("ai_explanation")
            result_dict["ai_recommendation"] = ai_data.get("ai_recommendation")
        return result_dict

    tasks = [_enhance_single(r) for r in results]
    return await asyncio.gather(*tasks)
