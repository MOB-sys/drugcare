"""DUR 병용금기 API 응답 파서 — 상호작용 데이터 변환."""

from typing import Any

from src.data.parsers.edrug_parser import strip_html_tags


# DUR API 응답 키 → 내부 키 매핑 (camelCase → snake_case)
_DUR_KEY_MAP: dict[str, str] = {
    "ITEM_SEQ": "item_seq",
    "ITEM_NAME": "item_name",
    "ENTP_NAME": "entp_name",
    "MAIN_INGR": "main_ingredient",
    "MIXTURE_ITEM_SEQ": "mixture_item_seq",
    "MIXTURE_ITEM_NAME": "mixture_item_name",
    "MIXTURE_ENTP_NAME": "mixture_entp_name",
    "MIXTURE_MAIN_INGR": "mixture_main_ingredient",
    "PROHBT_CONTENT": "prohibition_content",
    "REMARK": "remark",
    "TYPE_NAME": "type_name",
    # camelCase 변형 (API 버전에 따라 다를 수 있음)
    "itemSeq": "item_seq",
    "itemName": "item_name",
    "entpName": "entp_name",
    "mainIngr": "main_ingredient",
    "mixtureItemSeq": "mixture_item_seq",
    "mixtureItemName": "mixture_item_name",
    "mixtureEntpName": "mixture_entp_name",
    "mixtureMainIngr": "mixture_main_ingredient",
    "prohbtContent": "prohibition_content",
    "remark": "remark",
    "typeName": "type_name",
}


def _normalize_dur_item(raw_item: dict[str, Any]) -> dict[str, Any]:
    """DUR API 응답 아이템의 키를 snake_case로 정규화한다.

    Args:
        raw_item: DUR API 응답의 단일 아이템.

    Returns:
        정규화된 키를 가진 딕셔너리.
    """
    result: dict[str, Any] = {}

    for api_key, internal_key in _DUR_KEY_MAP.items():
        if api_key in raw_item:
            value = raw_item[api_key]
            if value is None or (isinstance(value, str) and not value.strip()):
                result[internal_key] = None
            else:
                result[internal_key] = str(value).strip() if isinstance(value, str) else value

    return result


def build_interaction_description(
    prohibition_content: str | None,
    remark: str | None,
) -> str:
    """금기 내용과 비고를 결합하여 상호작용 설명 텍스트를 생성한다.

    Args:
        prohibition_content: DUR 금기 내용 원문.
        remark: 비고 사항.

    Returns:
        정규화된 설명 텍스트.
    """
    parts: list[str] = []

    if prohibition_content:
        cleaned = strip_html_tags(prohibition_content)
        if cleaned:
            parts.append(cleaned)

    if remark:
        cleaned_remark = strip_html_tags(remark)
        if cleaned_remark:
            parts.append(f"[비고] {cleaned_remark}")

    return " | ".join(parts) if parts else "DUR 병용금기 (상세 설명 없음)"


def parse_dur_item(
    raw_item: dict[str, Any],
    drug_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    """DUR 병용금기 API 응답 아이템을 상호작용 테이블 삽입용 딕셔너리로 변환한다.

    두 약물의 item_seq가 모두 drug_lookup에 존재해야 유효한 상호작용으로 인정한다.

    Args:
        raw_item: DUR API 응답의 단일 아이템 딕셔너리.
        drug_lookup: item_seq → {"id": int, "name": str} 매핑 딕셔너리.
            DB에 존재하는 약물만 포함.

    Returns:
        interactions 테이블 삽입용 딕셔너리. 유효하지 않으면 None 반환.
        반환 형식:
        {
            "item_a_type": "drug",
            "item_a_id": int,
            "item_a_name": str,
            "item_b_type": "drug",
            "item_b_id": int,
            "item_b_name": str,
            "severity": "danger",
            "description": str,
            "source": "DUR",
            "source_id": str | None,
            "evidence_level": "official",
        }
    """
    normalized = _normalize_dur_item(raw_item)

    item_seq_a = normalized.get("item_seq")
    item_seq_b = normalized.get("mixture_item_seq")

    # 양쪽 품목기준코드가 모두 있어야 함
    if not item_seq_a or not item_seq_b:
        return None

    # 양쪽 모두 DB에 등록된 약물이어야 함
    drug_a = drug_lookup.get(str(item_seq_a))
    drug_b = drug_lookup.get(str(item_seq_b))

    if drug_a is None or drug_b is None:
        return None

    # 상호작용 설명 생성
    description = build_interaction_description(
        normalized.get("prohibition_content"),
        normalized.get("remark"),
    )

    # 정렬: item_a_id < item_b_id 순서로 통일 (중복 방지)
    if drug_a["id"] > drug_b["id"]:
        drug_a, drug_b = drug_b, drug_a

    # source_id: 두 item_seq 조합
    source_id = f"DUR_{item_seq_a}_{item_seq_b}"

    return {
        "item_a_type": "drug",
        "item_a_id": drug_a["id"],
        "item_a_name": drug_a["name"],
        "item_b_type": "drug",
        "item_b_id": drug_b["id"],
        "item_b_name": drug_b["name"],
        "severity": "danger",
        "description": description,
        "mechanism": None,
        "recommendation": "병용 투여를 피하십시오. 의사/약사와 상담하세요.",
        "source": "DUR",
        "source_id": source_id,
        "evidence_level": "official",
    }
