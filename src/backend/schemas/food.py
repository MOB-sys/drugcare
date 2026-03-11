"""식품 관련 API 스키마."""

from pydantic import BaseModel


class FoodSearchItem(BaseModel):
    """식품 검색 결과 아이템."""

    id: int
    name: str
    slug: str
    category: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class FoodDetail(BaseModel):
    """식품 상세 정보."""

    id: int
    name: str
    slug: str
    category: str | None = None
    description: str | None = None
    common_names: list[str] | None = None
    nutrients: list[dict] | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class FoodSearchResponse(BaseModel):
    """식품 검색 응답."""

    items: list[FoodSearchItem]
    total: int
    page: int
    page_size: int
