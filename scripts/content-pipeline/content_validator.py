"""콘텐츠 QA 검증 — 금지 표현, 면책조항, 의학적 주장 체크."""

from config import BANNED_EXPRESSIONS, REQUIRED_DISCLAIMER


def validate(content: str, title: str = "") -> tuple[bool, list[str]]:
    """콘텐츠를 검증하고 (통과 여부, 경고 목록)을 반환한다."""
    warnings: list[str] = []

    # 금지 표현 체크
    for expr in BANNED_EXPRESSIONS:
        if expr in content or expr in title:
            warnings.append(f"금지 표현 발견: '{expr}'")

    # 면책조항 체크
    if REQUIRED_DISCLAIMER not in content:
        warnings.append("면책조항 누락")

    # 최소 길이 체크
    if len(content) < 100:
        warnings.append(f"콘텐츠 너무 짧음 ({len(content)}자)")

    # 최대 길이 체크
    if len(content) > 5000:
        warnings.append(f"콘텐츠 너무 김 ({len(content)}자)")

    passed = not any("금지 표현" in w for w in warnings) and "면책조항 누락" not in [w for w in warnings]
    return passed, warnings
