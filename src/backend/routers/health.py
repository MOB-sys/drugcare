"""헬스체크 라우터 — DB 및 Redis 연결 상태 확인."""

import logging

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, HealthStatus
from src.backend.utils.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=ApiResponse[HealthStatus],
    summary="서비스 헬스체크",
    description="데이터베이스 및 Redis 연결 상태를 확인합니다.",
)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis),
) -> dict:
    """서비스 헬스체크 엔드포인트.

    DB와 Redis의 연결 상태를 각각 확인하여 반환한다.
    개별 컴포넌트 실패 시에도 200을 반환하되, 해당 컴포넌트를 'error'로 표시한다.

    Args:
        db: 비동기 DB 세션 (의존성 주입).
        redis_client: Redis 클라이언트 (의존성 주입).

    Returns:
        ApiResponse[HealthStatus] 포맷의 dict.
    """
    db_status = "ok"
    redis_status = "ok"
    overall_status = "healthy"

    # DB 연결 확인
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("헬스체크: DB 연결 실패 — %s: %s", type(exc).__name__, str(exc))
        db_status = "error"
        overall_status = "degraded"

    # Redis 연결 확인
    try:
        await redis_client.ping()
    except Exception as exc:
        logger.error("헬스체크: Redis 연결 실패 — %s: %s", type(exc).__name__, str(exc))
        redis_status = "error"
        overall_status = "degraded"

    health_data = HealthStatus(
        status=overall_status,
        database=db_status,
        redis=redis_status,
    )

    return success_response(health_data.model_dump())
