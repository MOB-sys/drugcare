"""상호작용 체크 라우터 — 약물/영양제 상호작용 확인."""

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse
from src.backend.schemas.interaction import (
    InteractionCheckRequest,
    InteractionCheckResponse,
)
from src.backend.services import interaction_service
from src.backend.utils.response import success_response

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post(
    "/check",
    response_model=ApiResponse[InteractionCheckResponse],
    summary="상호작용 체크",
    description="2개 이상의 약물/영양제 간 상호작용을 확인합니다.",
)
async def check_interactions(
    request_body: InteractionCheckRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """상호작용 체크 엔드포인트.

    요청된 아이템들 간의 모든 조합에 대해 상호작용을 확인한다.

    Args:
        request_body: 상호작용 체크 요청 (최소 2개 아이템 필수).
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[InteractionCheckResponse] 포맷의 dict.
    """
    result = await interaction_service.check_interactions(
        db, redis, request_body.items,
    )
    return success_response(result)
