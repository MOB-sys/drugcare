"""메트릭스 서비스 — Kill Criteria 추적 및 대시보드 데이터."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.app_metric import AppMetric
from src.backend.models.feedback import Feedback
from src.backend.schemas.metrics import MetricEventCreate

logger = logging.getLogger(__name__)


async def record_event(
    db: AsyncSession, device_id: str, data: MetricEventCreate
) -> dict:
    """메트릭 이벤트를 기록한다.

    Args:
        db: 비동기 DB 세션.
        device_id: 디바이스 식별자.
        data: 이벤트 데이터.

    Returns:
        기록된 이벤트 정보 dict.
    """
    metric = AppMetric(
        device_id=device_id,
        event_type=data.event_type,
        event_data=data.event_data,
        app_version=data.app_version,
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)

    return {
        "id": metric.id,
        "event_type": metric.event_type,
        "created_at": metric.created_at.isoformat(),
    }


async def get_dashboard(db: AsyncSession, period_days: int = 30) -> dict:
    """Kill Criteria 대시보드 데이터를 집계한다.

    Args:
        db: 비동기 DB 세션.
        period_days: 집계 기간 (일).

    Returns:
        대시보드 데이터 dict.
    """
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=period_days)
    week_start = now - timedelta(days=7)

    # 전체 디바이스 수
    total_devices_q = select(func.count(func.distinct(AppMetric.device_id))).where(
        AppMetric.created_at >= period_start
    )
    total_devices = (await db.execute(total_devices_q)).scalar() or 0

    # 7일 활성 디바이스 수
    active_7d_q = select(func.count(func.distinct(AppMetric.device_id))).where(
        AppMetric.created_at >= week_start
    )
    active_7d = (await db.execute(active_7d_q)).scalar() or 0

    # 전체 상호작용 체크 수
    total_checks_q = select(func.count()).where(
        AppMetric.event_type == "interaction_check",
        AppMetric.created_at >= period_start,
    ).select_from(AppMetric)
    total_checks = (await db.execute(total_checks_q)).scalar() or 0

    # 주간 상호작용 체크 수
    weekly_checks_q = select(func.count()).where(
        AppMetric.event_type == "interaction_check",
        AppMetric.created_at >= week_start,
    ).select_from(AppMetric)
    weekly_checks = (await db.execute(weekly_checks_q)).scalar() or 0

    # 전체 피드백 수
    total_feedbacks_q = select(func.count()).where(
        Feedback.created_at >= period_start,
    ).select_from(Feedback)
    total_feedbacks = (await db.execute(total_feedbacks_q)).scalar() or 0

    # 디바이스당 평균 이벤트 수
    avg_events = (total_checks / total_devices) if total_devices > 0 else 0.0

    return {
        "period_days": period_days,
        "total_devices": total_devices,
        "active_devices_7d": active_7d,
        "total_interaction_checks": total_checks,
        "weekly_interaction_checks": weekly_checks,
        "total_feedbacks": total_feedbacks,
        "avg_events_per_device": round(avg_events, 2),
    }
