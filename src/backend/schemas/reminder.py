"""리마인더(Reminder) 관련 API 스키마."""

from datetime import datetime, time

from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    """리마인더 생성 요청."""

    cabinet_item_id: int
    reminder_time: time
    days_of_week: list[int] = Field(..., min_length=1, max_length=7)
    memo: str | None = None


class ReminderUpdate(BaseModel):
    """리마인더 수정 요청 (부분 업데이트)."""

    reminder_time: time | None = None
    days_of_week: list[int] | None = Field(None, min_length=1, max_length=7)
    is_active: bool | None = None
    memo: str | None = None


class ReminderResponse(BaseModel):
    """리마인더 응답."""

    id: int
    device_id: str
    cabinet_item_id: int
    item_name: str
    reminder_time: time
    days_of_week: list[int]
    is_active: bool
    memo: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
