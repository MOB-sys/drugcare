"""API 응답 헬퍼 단위 테스트 — success_response / error_response 포맷 검증."""

from datetime import datetime, timezone

import pytest

from src.backend.utils.response import error_response, success_response


# ---------------------------------------------------------------------------
# success_response
# ---------------------------------------------------------------------------


def test_success_response_format():
    """success_response는 ApiResponse 표준 포맷을 반환한다."""
    result = success_response({"items": [1, 2, 3]})

    assert result["success"] is True
    assert result["data"] == {"items": [1, 2, 3]}
    assert result["error"] is None
    assert "timestamp" in result["meta"]


def test_success_response_timestamp_utc_iso():
    """success_response의 timestamp는 UTC ISO 8601 형식이다."""
    result = success_response(None)
    ts = result["meta"]["timestamp"]

    # ISO 형식 파싱 가능 여부 확인
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None or "+" in ts or "Z" in ts


def test_success_response_none_data():
    """data가 None이어도 정상적으로 래핑된다."""
    result = success_response(None)
    assert result["success"] is True
    assert result["data"] is None


# ---------------------------------------------------------------------------
# error_response
# ---------------------------------------------------------------------------


def test_error_response_format():
    """error_response는 ApiResponse 에러 포맷의 JSONResponse를 반환한다."""
    resp = error_response(message="잘못된 요청입니다.", status_code=400)

    assert resp.status_code == 400
    body = resp.body.decode("utf-8")
    import json
    content = json.loads(body)

    assert content["success"] is False
    assert content["data"] is None
    assert content["error"] == "잘못된 요청입니다."
    assert "timestamp" in content["meta"]


def test_error_response_default_status_code():
    """status_code 미지정 시 기본값 400을 사용한다."""
    resp = error_response(message="에러")
    assert resp.status_code == 400


def test_error_response_custom_status_code():
    """커스텀 status_code가 올바르게 적용된다."""
    resp = error_response(message="서버 오류", status_code=500)
    assert resp.status_code == 500


def test_error_response_timestamp_utc_iso():
    """error_response의 timestamp는 UTC ISO 8601 형식이다."""
    resp = error_response(message="에러")
    import json
    content = json.loads(resp.body.decode("utf-8"))
    ts = content["meta"]["timestamp"]

    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None or "+" in ts or "Z" in ts
