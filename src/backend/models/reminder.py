"""리마인더(Reminder) 모델 — 복약 알림 스케줄."""

from datetime import time

from sqlalchemy import BigInteger, Boolean, Index, String, Time
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base, TimestampMixin


class Reminder(Base, TimestampMixin):
    """복약 리마인더 테이블.

    Attributes:
        id: 내부 PK
        device_id: 디바이스 UUID
        cabinet_item_id: 복약함 아이템 참조 ID
        item_name: 아이템명 (비정규화)
        reminder_time: 알림 시각
        days_of_week: 요일 배열 [0=월, ..., 6=일]
        is_active: 활성 여부
        memo: 메모
    """

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    cabinet_item_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    item_name: Mapped[str] = mapped_column(String(500), nullable=False)
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    days_of_week: Mapped[list[int]] = mapped_column(ARRAY(BigInteger), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    memo: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (
        Index("ix_reminders_device_active", "device_id", "is_active"),
    )

    def __repr__(self) -> str:
        """리마인더 모델의 문자열 표현을 반환한다."""
        return (
            f"<Reminder(id={self.id}, device={self.device_id}, "
            f"item={self.item_name!r}, time={self.reminder_time})>"
        )
