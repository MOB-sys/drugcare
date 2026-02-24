"""의약품 관련 API 스키마."""

from pydantic import BaseModel


class IngredientInfo(BaseModel):
    """성분 정보."""

    name: str
    amount: str | None = None
    unit: str | None = None


class DrugSearchItem(BaseModel):
    """약물 검색 결과 아이템."""

    id: int
    item_seq: str
    item_name: str
    entp_name: str | None = None
    etc_otc_code: str | None = None
    class_no: str | None = None
    item_image: str | None = None

    model_config = {"from_attributes": True}


class DrugDetail(BaseModel):
    """약물 상세 정보."""

    id: int
    item_seq: str
    item_name: str
    entp_name: str | None = None
    etc_otc_code: str | None = None
    class_no: str | None = None
    chart: str | None = None
    bar_code: str | None = None
    material_name: str | None = None
    ingredients: list[IngredientInfo] | None = None
    efcy_qesitm: str | None = None
    use_method_qesitm: str | None = None
    atpn_warn_qesitm: str | None = None
    atpn_qesitm: str | None = None
    intrc_qesitm: str | None = None
    se_qesitm: str | None = None
    deposit_method_qesitm: str | None = None
    item_image: str | None = None

    model_config = {"from_attributes": True}
