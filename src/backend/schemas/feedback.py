"""피드백 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """피드백 생성 요청."""

    category: str = Field(
        ...,
        max_length=32,
        description="피드백 카테고리 (bug, feature, data_error, other)",
    )
    content: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="피드백 내용",
    )
    app_version: str = Field(default="1.0.0", max_length=20)
    os_info: str | None = Field(default=None, max_length=50)


class FeedbackResponse(BaseModel):
    """피드백 응답."""

    model_config = {"from_attributes": True}

    id: int
    category: str
    content: str
    app_version: str
    created_at: datetime
