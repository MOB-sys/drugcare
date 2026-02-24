"""e약은요 API 응답 파서 — HTML 태그 제거 및 데이터 정규화."""

import re
from typing import Any


# HTML 태그 제거 정규식 (컴파일하여 재사용)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_NEWLINE_NORMALIZE_RE = re.compile(r"\n{3,}")


def strip_html_tags(text: str | None) -> str | None:
    """HTML 태그를 제거하고 공백을 정규화한다.

    Args:
        text: HTML 태그가 포함될 수 있는 원본 텍스트.

    Returns:
        태그가 제거된 정규화된 텍스트. 입력이 None이면 None 반환.
    """
    if text is None:
        return None

    # HTML 태그 제거
    cleaned = _HTML_TAG_RE.sub(" ", text)

    # HTML 엔티티 치환
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = cleaned.replace("&lt;", "<")
    cleaned = cleaned.replace("&gt;", ">")
    cleaned = cleaned.replace("&nbsp;", " ")
    cleaned = cleaned.replace("&quot;", '"')

    # 연속 공백을 단일 공백으로
    cleaned = _WHITESPACE_RE.sub(" ", cleaned)

    # 앞뒤 공백 제거
    cleaned = cleaned.strip()

    return cleaned if cleaned else None


def normalize_whitespace(text: str | None) -> str | None:
    """문자열의 공백을 정규화한다.

    연속된 공백/탭/개행을 단일 공백으로 치환하고 앞뒤 공백을 제거한다.

    Args:
        text: 정규화할 문자열.

    Returns:
        정규화된 문자열. 입력이 None이면 None 반환.
    """
    if text is None:
        return None

    normalized = _WHITESPACE_RE.sub(" ", text).strip()
    return normalized if normalized else None


def parse_material_name(material_name: str | None) -> list[dict[str, str | None]]:
    """원료성분 텍스트를 구조화된 성분 리스트로 파싱한다.

    e약은요 API의 material_name 필드 형식:
    "성분명1|분량1|단위1|...,성분명2|분량2|단위2|..."

    일반적인 형식이 아닌 경우 세미콜론(;) 또는 쉼표(,) 구분도 시도한다.

    Args:
        material_name: 원료성분 원본 텍스트.

    Returns:
        성분 딕셔너리 리스트. [{"name": ..., "amount": ..., "unit": ...}]
    """
    if not material_name:
        return []

    ingredients: list[dict[str, str | None]] = []

    # 파이프(|) 구분 형식 시도: "성분명|분량|단위|..."
    if "|" in material_name:
        # 쉼표 또는 세미콜론으로 각 성분 분리
        separator = ";" if ";" in material_name else ","
        parts = material_name.split(separator)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            fields = [f.strip() for f in part.split("|")]
            if len(fields) >= 1 and fields[0]:
                ingredient: dict[str, str | None] = {"name": fields[0]}
                ingredient["amount"] = fields[1] if len(fields) > 1 and fields[1] else None
                ingredient["unit"] = fields[2] if len(fields) > 2 and fields[2] else None
                ingredients.append(ingredient)
    else:
        # 파이프가 없는 단순 텍스트 — 전체를 하나의 성분으로
        cleaned = strip_html_tags(material_name)
        if cleaned:
            ingredients.append({"name": cleaned, "amount": None, "unit": None})

    return ingredients


# e약은요 API 응답의 텍스트 필드 목록 (HTML 태그 제거 대상)
_TEXT_FIELDS = (
    "efcy_qesitm",
    "use_method_qesitm",
    "atpn_warn_qesitm",
    "atpn_qesitm",
    "intrc_qesitm",
    "se_qesitm",
    "deposit_method_qesitm",
    "chart",
)

# e약은요 API 응답 키 → DB 컬럼 매핑 (API 키는 대문자 혼용)
_API_KEY_MAP: dict[str, str] = {
    "ITEM_SEQ": "item_seq",
    "ITEM_NAME": "item_name",
    "ENTP_NAME": "entp_name",
    "ETC_OTC_CODE": "etc_otc_code",
    "CLASS_NO": "class_no",
    "CHART": "chart",
    "BAR_CODE": "bar_code",
    "MATERIAL_NAME": "material_name",
    "EE_DOC_DATA": "efcy_qesitm",
    "UD_DOC_DATA": "use_method_qesitm",
    "NB_DOC_DATA": "atpn_warn_qesitm",
    # e약은요 getDrbEasyDrugList 전용 키
    "itemSeq": "item_seq",
    "itemName": "item_name",
    "entpName": "entp_name",
    "etcOtcCode": "etc_otc_code",
    "classNo": "class_no",
    "chart": "chart",
    "barCode": "bar_code",
    "materialName": "material_name",
    "efcyQesitm": "efcy_qesitm",
    "useMethodQesitm": "use_method_qesitm",
    "atpnWarnQesitm": "atpn_warn_qesitm",
    "atpnQesitm": "atpn_qesitm",
    "intrcQesitm": "intrc_qesitm",
    "seQesitm": "se_qesitm",
    "depositMethodQesitm": "deposit_method_qesitm",
    "itemImage": "item_image",
}


def parse_drug_item(raw_item: dict[str, Any]) -> dict[str, Any]:
    """e약은요 API 응답의 단일 아이템을 DB 저장용 딕셔너리로 변환한다.

    수행 작업:
    1. API 키를 DB 컬럼명으로 매핑
    2. 텍스트 필드의 HTML 태그 제거
    3. material_name을 구조화된 ingredients로 파싱

    Args:
        raw_item: e약은요 API 응답의 단일 아이템 딕셔너리.

    Returns:
        DB 삽입/업데이트에 사용할 정규화된 딕셔너리.
    """
    result: dict[str, Any] = {}

    # API 키 매핑
    for api_key, db_col in _API_KEY_MAP.items():
        if api_key in raw_item:
            value = raw_item[api_key]
            # None이나 빈 문자열 처리
            if value is None or (isinstance(value, str) and not value.strip()):
                result[db_col] = None
            else:
                result[db_col] = str(value).strip() if isinstance(value, str) else value

    # 텍스트 필드 HTML 태그 제거
    for field in _TEXT_FIELDS:
        if field in result and result[field] is not None:
            result[field] = strip_html_tags(result[field])

    # material_name → ingredients 구조화
    material_name_raw = result.get("material_name")
    result["ingredients"] = parse_material_name(material_name_raw)

    # material_name 자체도 HTML 태그 제거 (이미 ingredients로 파싱 후)
    if "material_name" in result and result["material_name"]:
        result["material_name"] = strip_html_tags(result["material_name"])

    return result
