"""리뷰 관련 API 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """리뷰 생성/수정 요청."""

    rating: int = Field(..., ge=1, le=5, description="전체 평점 (1-5)")
    effectiveness: int | None = Field(None, ge=1, le=5, description="효과 평점")
    ease_of_use: int | None = Field(None, ge=1, le=5, description="복용 편의성 평점")
    comment: str | None = Field(None, max_length=500, description="리뷰 코멘트")


class ReviewResponse(BaseModel):
    """리뷰 응답."""

    id: int
    device_id: str
    item_type: str
    item_id: int
    rating: int
    effectiveness: int | None = None
    ease_of_use: int | None = None
    comment: str | None = None
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    """리뷰 요약 통계."""

    average_rating: float
    total_count: int
    distribution: dict[str, int]
