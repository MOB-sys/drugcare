"""상호작용 체크 서비스 — 핵심 비즈니스 로직."""

import json
from itertools import combinations

from redis.asyncio import Redis
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings
from src.backend.core.redis import CACHE_TTL_INTERACTION
from src.backend.models.interaction import Interaction, Severity
from src.backend.schemas.interaction import (
    InteractionCheckResponse,
    InteractionItem,
    InteractionResult,
)
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key

settings = get_settings()

# 심각도 정렬 순서: danger(0) → warning(1) → caution(2) → info(3)
_SEVERITY_ORDER: dict[Severity, int] = {
    Severity.DANGER: 0,
    Severity.WARNING: 1,
    Severity.CAUTION: 2,
    Severity.INFO: 3,
}


async def check_interactions(
    db: AsyncSession,
    redis: Redis,
    items: list[InteractionItem],
) -> dict:
    """아이템 목록의 모든 쌍에 대해 상호작용을 체크한다.

    nC2 조합으로 모든 쌍을 생성하고, 양방향 매칭으로 DB를 조회한다.
    Redis 캐시를 우선 확인하며, 결과는 심각도 순으로 정렬된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        items: 상호작용을 확인할 아이템 목록 (최소 2개).

    Returns:
        InteractionCheckResponse 구조의 dict.
    """
    # 캐시 키 생성 — 순서 무관하도록 정렬
    sorted_key_data = sorted(
        [(it.item_type.value, it.item_id) for it in items],
    )
    cache_key = make_cache_key(
        "interaction",
        "check",
        hash_query(json.dumps(sorted_key_data)),
    )

    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # nC2 쌍 생성
    pairs = list(combinations(items, 2))

    if not pairs:
        return _build_empty_response()

    # 모든 쌍에 대한 양방향 OR 조건 생성
    conditions = _build_pair_conditions(pairs)

    stmt = select(Interaction).where(or_(*conditions))
    rows = await db.execute(stmt)
    interactions = rows.scalars().all()

    # 결과 변환 및 심각도순 정렬
    results_list = _to_sorted_results(interactions)

    has_danger = any(r.severity == Severity.DANGER for r in results_list)

    response = InteractionCheckResponse(
        total_checked=len(pairs),
        interactions_found=len(results_list),
        has_danger=has_danger,
        results=results_list,
    )
    response_dict = response.model_dump()

    # AI 설명 추가 (API 키가 설정된 경우에만)
    if settings.OPENAI_API_KEY:
        try:
            from src.backend.services.ai_explanation_service import enhance_results

            enhanced = await enhance_results(redis, results_list)
            response_dict["results"] = enhanced
        except Exception:
            import logging

            logging.getLogger(__name__).warning("AI 설명 생성 실패 — 기본 결과 반환", exc_info=True)

    await cache_set(redis, cache_key, response_dict, CACHE_TTL_INTERACTION)
    return response_dict


def _build_pair_conditions(pairs: list[tuple[InteractionItem, InteractionItem]]) -> list:
    """아이템 쌍 목록으로부터 양방향 SQLAlchemy 조건을 생성한다.

    Args:
        pairs: (아이템A, 아이템B) 쌍 목록.

    Returns:
        SQLAlchemy and_/or_ 조건 리스트.
    """
    conditions = []
    for a, b in pairs:
        conditions.append(
            and_(
                Interaction.item_a_type == a.item_type,
                Interaction.item_a_id == a.item_id,
                Interaction.item_b_type == b.item_type,
                Interaction.item_b_id == b.item_id,
            ),
        )
        conditions.append(
            and_(
                Interaction.item_a_type == b.item_type,
                Interaction.item_a_id == b.item_id,
                Interaction.item_b_type == a.item_type,
                Interaction.item_b_id == a.item_id,
            ),
        )
    return conditions


def _to_sorted_results(interactions: list[Interaction]) -> list[InteractionResult]:
    """Interaction 모델 목록을 심각도순 InteractionResult로 변환한다.

    Args:
        interactions: DB에서 조회한 Interaction 레코드 목록.

    Returns:
        심각도 순(danger→info)으로 정렬된 InteractionResult 리스트.
    """
    results = [InteractionResult.model_validate(row) for row in interactions]
    results.sort(key=lambda r: _SEVERITY_ORDER.get(r.severity, 99))
    return results


def _build_empty_response() -> dict:
    """빈 상호작용 응답을 생성한다.

    Returns:
        InteractionCheckResponse 구조의 빈 dict.
    """
    return InteractionCheckResponse(
        total_checked=0,
        interactions_found=0,
        has_danger=False,
        results=[],
    ).model_dump()
