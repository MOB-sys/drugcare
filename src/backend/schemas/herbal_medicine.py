"""한약재(생약) 관련 API 스키마."""

from pydantic import BaseModel


class HerbalMedicineSearchItem(BaseModel):
    """한약재 검색 결과 아이템."""

    id: int
    name: str
    slug: str
    korean_name: str | None = None
    category: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class HerbalMedicineDetail(BaseModel):
    """한약재 상세 정보."""

    id: int
    name: str
    slug: str
    korean_name: str | None = None
    latin_name: str | None = None
    category: str | None = None
    properties: dict | None = None
    description: str | None = None
    efficacy: str | None = None
    precautions: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class HerbalMedicineSearchResponse(BaseModel):
    """한약재 검색 응답."""

    items: list[HerbalMedicineSearchItem]
    total: int
    page: int
    page_size: int
