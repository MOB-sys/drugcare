"""상호작용 체크 API 스키마."""

from pydantic import BaseModel, Field

from src.backend.models.interaction import ItemType, Severity


class InteractionItem(BaseModel):
    """상호작용 체크 요청의 단일 아이템."""

    item_type: ItemType
    item_id: int


class InteractionCheckRequest(BaseModel):
    """상호작용 체크 요청.

    최소 2개 아이템을 받아 상호작용을 확인한다.
    """

    items: list[InteractionItem] = Field(..., min_length=2, max_length=20)


class InteractionResult(BaseModel):
    """단일 상호작용 결과."""

    item_a_name: str
    item_b_name: str
    severity: Severity
    description: str | None = None
    mechanism: str | None = None
    recommendation: str | None = None
    source: str
    evidence_level: str | None = None
    ai_explanation: str | None = None
    ai_recommendation: str | None = None


class InteractionCheckResponse(BaseModel):
    """상호작용 체크 응답."""

    total_checked: int
    interactions_found: int
    has_danger: bool
    results: list[InteractionResult]
    disclaimer: str = "이 정보는 참고용이며, 의사/약사의 전문적 판단을 대체하지 않습니다."
