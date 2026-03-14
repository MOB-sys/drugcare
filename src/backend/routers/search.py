"""통합 검색 라우터 — 전체 타입 자동완성 및 통합 검색."""

import asyncio

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse
from src.backend.services import (
    drug_service,
    food_service,
    herbal_medicine_service,
    supplement_service,
)
from src.backend.utils.response import success_response

router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "/suggest",
    response_model=ApiResponse[list[dict]],
    summary="통합 검색 자동완성",
    description="약물, 영양제, 식품, 한약재를 통합 검색하여 자동완성 제안을 반환합니다.",
)
async def suggest_all(
    q: str = Query("", min_length=2, max_length=100, description="검색어 (2자 이상)"),
    limit: int = Query(10, ge=1, le=30, description="최대 결과 수 (타입별 균등 분배)"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """전체 타입 통합 자동완성 엔드포인트.

    약물, 영양제, 식품, 한약재에서 각 타입당 최대 limit/4개씩 병렬 검색하여
    관련성 높은 순으로 합쳐서 반환한다.
    """
    per_type = max(2, (limit + 3) // 4)

    drugs, supplements, foods, herbals = await asyncio.gather(
        drug_service.suggest_drugs(db, redis, q, per_type),
        supplement_service.suggest_supplements(db, redis, q, per_type),
        food_service.suggest_foods(db, redis, q, per_type),
        herbal_medicine_service.suggest_herbal_medicines(db, redis, q, per_type),
    )

    combined = drugs + supplements + foods + herbals
    return success_response(combined[:limit])
