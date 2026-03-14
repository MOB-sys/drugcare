"""메트릭스 스키마."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def validate_event_data(self) -> "MetricEventCreate":
        """event_data 크기 제약을 검증한다."""
        if self.event_data is None:
            return self

        # 최대 20개 키
        if len(self.event_data) > 20:
            raise ValueError("event_data는 최대 20개 키만 허용됩니다")

        # 문자열 값 최대 500자
        for key, value in self.event_data.items():
            if isinstance(value, str) and len(value) > 500:
                raise ValueError(f"event_data 문자열 값은 최대 500자입니다 (키: {key})")

        # 직렬화 크기 10KB 미만
        serialized = json.dumps(self.event_data, ensure_ascii=False, default=str)
        if len(serialized.encode("utf-8")) >= 10240:
            raise ValueError("event_data 직렬화 크기는 10KB 미만이어야 합니다")

        return self


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
