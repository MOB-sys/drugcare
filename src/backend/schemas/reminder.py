"""리마인더(Reminder) 관련 API 스키마."""

from datetime import datetime, time

from pydantic import BaseModel, Field, field_validator


class ReminderCreate(BaseModel):
    """리마인더 생성 요청."""

    cabinet_item_id: int
    reminder_time: time
    days_of_week: list[int] = Field(..., min_length=1, max_length=7)
    memo: str | None = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: list[int]) -> list[int]:
        """요일 값이 0~6 범위인지 검증한다."""
        for day in v:
            if day < 0 or day > 6:
                raise ValueError(f"days_of_week 값은 0~6이어야 합니다 (입력값: {day})")
        return v


class ReminderUpdate(BaseModel):
    """리마인더 수정 요청 (부분 업데이트)."""

    reminder_time: time | None = None
    days_of_week: list[int] | None = Field(None, min_length=1, max_length=7)
    is_active: bool | None = None
    memo: str | None = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v: list[int] | None) -> list[int] | None:
        """요일 값이 0~6 범위인지 검증한다."""
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError(f"days_of_week 값은 0~6이어야 합니다 (입력값: {day})")
        return v


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
