"""영양제(건강기능식품) 관련 API 스키마."""

from pydantic import BaseModel


class SupplementSearchItem(BaseModel):
    """영양제 검색 결과 아이템."""

    id: int
    product_name: str
    slug: str
    company: str | None = None
    main_ingredient: str | None = None
    category: str | None = None

    model_config = {"from_attributes": True}


class SupplementDetail(BaseModel):
    """영양제 상세 정보."""

    id: int
    product_name: str
    slug: str
    company: str | None = None
    registration_no: str | None = None
    main_ingredient: str | None = None
    ingredients: list[dict] | None = None
    functionality: str | None = None
    precautions: str | None = None
    intake_method: str | None = None
    category: str | None = None
    source: str | None = None

    model_config = {"from_attributes": True}
