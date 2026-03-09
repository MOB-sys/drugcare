"""복약함(Cabinet) 관련 API 스키마."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.backend.models.user_cabinet import CabinetItemType


class CabinetItemCreate(BaseModel):
    """복약함 아이템 추가 요청."""

    item_type: CabinetItemType
    item_id: int = Field(..., gt=0)
    nickname: str | None = None


class CabinetItemResponse(BaseModel):
    """복약함 아이템 응답."""

    id: int
    item_type: CabinetItemType
    item_id: int
    item_name: str
    nickname: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
