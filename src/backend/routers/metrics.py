"""메트릭스 라우터 — 앱 사용 이벤트 기록 및 Kill Criteria 대시보드."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.schemas.common import ApiResponse
from src.backend.schemas.metrics import (
    KillCriteriaDashboard,
    MetricEventCreate,
    MetricEventResponse,
)
from src.backend.services import metrics_service
from src.backend.utils.response import success_response

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _get_device_id(request: Request) -> str:
    """요청에서 device_id를 안전하게 추출한다."""
    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise ValueError("device_id")
    return device_id


@router.post(
    "/event",
    response_model=ApiResponse[MetricEventResponse],
    summary="메트릭 이벤트 기록",
    description="앱 사용 이벤트를 기록합니다 (app_open, interaction_check, search 등).",
)
async def record_metric_event(
    data: MetricEventCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """메트릭 이벤트 기록 엔드포인트.

    Args:
        data: 이벤트 정보 (event_type, event_data, app_version).
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[MetricEventResponse] 포맷의 dict.
    """
    device_id = _get_device_id(request)
    result = await metrics_service.record_event(db, device_id, data)
    return success_response(result)


@router.get(
    "/dashboard",
    response_model=ApiResponse[KillCriteriaDashboard],
    summary="Kill Criteria 대시보드",
    description="Kill Criteria 모니터링을 위한 집계 데이터를 반환합니다.",
)
async def get_kill_criteria_dashboard(
    period_days: int = Query(default=30, ge=1, le=365, description="집계 기간 (일)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Kill Criteria 대시보드 엔드포인트.

    Args:
        period_days: 집계 기간 (기본 30일).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[KillCriteriaDashboard] 포맷의 dict.
    """
    result = await metrics_service.get_dashboard(db, period_days)
    return success_response(result)
