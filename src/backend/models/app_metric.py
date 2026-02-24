"""앱 메트릭스 모델 — Kill Criteria 추적용 이벤트 기록."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.models.base import Base


class AppMetric(Base):
    """앱 사용 이벤트 메트릭스 테이블."""

    __tablename__ = "app_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    app_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
