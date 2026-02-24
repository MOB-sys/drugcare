"""의약품 데이터 검증 — 필수 필드, 형식, 중복 체크."""

import re
from typing import Any

# 품목기준코드 형식: 숫자 9~15자리
_ITEM_SEQ_RE = re.compile(r"^\d{9,15}$")

# 필수 필드 목록
_REQUIRED_FIELDS = ("item_seq", "item_name")


def validate_drug(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """의약품 데이터의 유효성을 검증한다.

    검증 항목:
    1. 필수 필드 존재 여부 (item_seq, item_name)
    2. item_seq 형식 (숫자 9~15자리)
    3. item_name 길이 (1~500자)
    4. etc_otc_code 유효값 (전문/일반)
    5. class_no 형식 (숫자)

    Args:
        data: 검증할 의약품 데이터 딕셔너리.

    Returns:
        (is_valid, errors) 튜플.
        is_valid: 모든 검증 통과 시 True.
        errors: 발견된 오류 메시지 리스트.
    """
    errors: list[str] = []

    # 1. 필수 필드 존재 여부
    for field in _REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"필수 필드 누락: {field}")

    # 2. item_seq 형식 검증
    item_seq = data.get("item_seq")
    if item_seq is not None and isinstance(item_seq, str) and item_seq.strip():
        if not _ITEM_SEQ_RE.match(item_seq.strip()):
            errors.append(
                f"item_seq 형식 오류: '{item_seq}' (숫자 9~15자리 필요)"
            )

    # 3. item_name 길이 검증
    item_name = data.get("item_name")
    if item_name is not None and isinstance(item_name, str):
        name_len = len(item_name.strip())
        if name_len == 0:
            errors.append("item_name이 비어있습니다.")
        elif name_len > 500:
            errors.append(
                f"item_name 길이 초과: {name_len}자 (최대 500자)"
            )

    # 4. etc_otc_code 유효값 검증 (선택 필드)
    etc_otc_code = data.get("etc_otc_code")
    if etc_otc_code is not None and isinstance(etc_otc_code, str) and etc_otc_code.strip():
        valid_codes = {"전문의약품", "일반의약품", "전문", "일반"}
        if etc_otc_code.strip() not in valid_codes:
            errors.append(
                f"etc_otc_code 유효하지 않은 값: '{etc_otc_code}' "
                f"(허용: {valid_codes})"
            )

    # 5. class_no 형식 검증 (선택 필드)
    class_no = data.get("class_no")
    if class_no is not None and isinstance(class_no, str) and class_no.strip():
        if not class_no.strip().isdigit():
            errors.append(
                f"class_no 형식 오류: '{class_no}' (숫자만 허용)"
            )

    is_valid = len(errors) == 0
    return is_valid, errors


def check_duplicate(item_seq: str, existing_seqs: set[str]) -> bool:
    """해당 품목기준코드가 이미 존재하는지 확인한다.

    Args:
        item_seq: 확인할 품목기준코드.
        existing_seqs: 이미 존재하는 품목기준코드 집합.

    Returns:
        True이면 중복 존재, False이면 신규.
    """
    return item_seq in existing_seqs
