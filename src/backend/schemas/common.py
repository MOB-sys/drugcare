"""API 표준 응답 스키마."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaInfo(BaseModel):
    """응답 메타 정보."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiResponse(BaseModel, Generic[T]):
    """API 표준 응답 포맷.

    Example:
        {"success": true, "data": {...}, "error": null, "meta": {"timestamp": "..."}}
    """

    success: bool
    data: T | None = None
    error: str | None = None
    meta: MetaInfo = Field(default_factory=MetaInfo)


class PaginatedData(BaseModel, Generic[T]):
    """페이지네이션 래퍼."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthStatus(BaseModel):
    """헬스체크 응답 데이터."""

    status: str = "healthy"
    database: str = "ok"
    redis: str = "ok"
