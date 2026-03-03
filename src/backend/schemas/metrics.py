"""메트릭스 스키마."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MetricEventCreate(BaseModel):
    """메트릭 이벤트 기록 요청."""

    event_type: str = Field(
        ...,
        max_length=50,
        description="이벤트 유형 (app_open, interaction_check, search, cabinet_add 등)",
    )
    event_data: dict[str, Any] | None = Field(
        default=None,
        description="이벤트 부가 데이터",
    )
    app_version: str = Field(default="1.0.0", max_length=20)


class MetricEventResponse(BaseModel):
    """메트릭 이벤트 응답."""

    model_config = {"from_attributes": True}

    id: int
    event_type: str
    created_at: datetime


class KillCriteriaDashboard(BaseModel):
    """Kill Criteria 대시보드 데이터."""

    period_days: int
    total_devices: int
    active_devices_7d: int
    total_interaction_checks: int
    weekly_interaction_checks: int
    total_feedbacks: int
    avg_events_per_device: float
