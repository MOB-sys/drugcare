"""상호작용 데이터 검증 — 필수 필드, 참조 무결성, 중복 체크."""

from typing import Any

# 허용되는 심각도 값
_VALID_SEVERITIES = {"danger", "warning", "caution", "info"}

# 허용되는 아이템 유형
_VALID_ITEM_TYPES = {"drug", "supplement"}

# 허용되는 데이터 출처
_VALID_SOURCES = {"DUR", "DrugBank", "NaturalMedicines", "자체구축", "AI생성"}

# 허용되는 근거 수준
_VALID_EVIDENCE_LEVELS = {"official", "high", "medium", "low", "unknown"}

# 필수 필드 목록
_REQUIRED_FIELDS = (
    "item_a_type",
    "item_a_id",
    "item_a_name",
    "item_b_type",
    "item_b_id",
    "item_b_name",
    "severity",
    "source",
)


def validate_interaction(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """상호작용 데이터의 유효성을 검증한다.

    검증 항목:
    1. 필수 필드 존재 여부
    2. item_type 유효값
    3. severity 유효값
    4. source 유효값
    5. 자기 참조 방지 (같은 아이템끼리의 상호작용)
    6. item_id 양수 확인

    Args:
        data: 검증할 상호작용 데이터 딕셔너리.

    Returns:
        (is_valid, errors) 튜플.
        is_valid: 모든 검증 통과 시 True.
        errors: 발견된 오류 메시지 리스트.
    """
    errors: list[str] = []

    # 1. 필수 필드 존재 여부
    for field in _REQUIRED_FIELDS:
        value = data.get(field)
        if value is None:
            errors.append(f"필수 필드 누락: {field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"필수 필드가 비어있음: {field}")

    # 2. item_type 유효값 검증
    for type_field in ("item_a_type", "item_b_type"):
        item_type = data.get(type_field)
        if item_type is not None and item_type not in _VALID_ITEM_TYPES:
            errors.append(
                f"{type_field} 유효하지 않은 값: '{item_type}' "
                f"(허용: {_VALID_ITEM_TYPES})"
            )

    # 3. severity 유효값 검증
    severity = data.get("severity")
    if severity is not None and severity not in _VALID_SEVERITIES:
        errors.append(
            f"severity 유효하지 않은 값: '{severity}' "
            f"(허용: {_VALID_SEVERITIES})"
        )

    # 4. source 유효값 검증
    source = data.get("source")
    if source is not None and source not in _VALID_SOURCES:
        errors.append(
            f"source 유효하지 않은 값: '{source}' "
            f"(허용: {_VALID_SOURCES})"
        )

    # 4-1. evidence_level 유효값 검증
    evidence_level = data.get("evidence_level")
    if evidence_level is not None and evidence_level not in _VALID_EVIDENCE_LEVELS:
        errors.append(
            f"evidence_level 유효하지 않은 값: '{evidence_level}' "
            f"(허용: {_VALID_EVIDENCE_LEVELS})"
        )

    # 5. 자기 참조 방지
    item_a_type = data.get("item_a_type")
    item_a_id = data.get("item_a_id")
    item_b_type = data.get("item_b_type")
    item_b_id = data.get("item_b_id")

    if (
        item_a_type is not None
        and item_b_type is not None
        and item_a_id is not None
        and item_b_id is not None
        and item_a_type == item_b_type
        and item_a_id == item_b_id
    ):
        errors.append("자기 참조 상호작용 불가: A와 B가 동일한 아이템입니다.")

    # 6. item_id 양수 확인
    for id_field in ("item_a_id", "item_b_id"):
        item_id = data.get(id_field)
        if item_id is not None and isinstance(item_id, int) and item_id <= 0:
            errors.append(f"{id_field}는 양수여야 합니다: {item_id}")

    is_valid = len(errors) == 0
    return is_valid, errors


def check_referential_integrity(
    data: dict[str, Any],
    drug_ids: set[int],
    supplement_ids: set[int],
) -> tuple[bool, list[str]]:
    """상호작용 데이터의 참조 무결성을 검증한다.

    각 아이템의 type에 따라 해당 테이블에 ID가 존재하는지 확인한다.

    Args:
        data: 검증할 상호작용 데이터 딕셔너리.
        drug_ids: DB에 존재하는 약물 ID 집합.
        supplement_ids: DB에 존재하는 영양제 ID 집합.

    Returns:
        (is_valid, errors) 튜플.
        is_valid: 참조 무결성이 모두 유효하면 True.
        errors: 발견된 오류 메시지 리스트.
    """
    errors: list[str] = []

    for side in ("a", "b"):
        item_type = data.get(f"item_{side}_type")
        item_id = data.get(f"item_{side}_id")
        item_name = data.get(f"item_{side}_name", "알수없음")

        if item_type is None or item_id is None:
            continue

        if item_type == "drug":
            if item_id not in drug_ids:
                errors.append(
                    f"item_{side} 참조 오류: drug ID {item_id} "
                    f"({item_name})이(가) drugs 테이블에 없습니다."
                )
        elif item_type == "supplement":
            if item_id not in supplement_ids:
                errors.append(
                    f"item_{side} 참조 오류: supplement ID {item_id} "
                    f"({item_name})이(가) supplements 테이블에 없습니다."
                )

    is_valid = len(errors) == 0
    return is_valid, errors
