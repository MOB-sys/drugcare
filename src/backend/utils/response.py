"""API 응답 헬퍼 함수 — 표준 ApiResponse 포맷 래핑."""

from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse


def success_response(data: Any) -> dict:
    """성공 응답을 ApiResponse 표준 포맷으로 래핑한다.

    Args:
        data: 응답 데이터 (dict, list, Pydantic model 등).

    Returns:
        ApiResponse 포맷의 dict.
    """
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
    }


def error_response(message: str, status_code: int = 400) -> JSONResponse:
    """에러 응답을 ApiResponse 표준 포맷의 JSONResponse로 반환한다.

    Args:
        message: 에러 메시지.
        status_code: HTTP 상태 코드 (기본 400).

    Returns:
        JSONResponse with ApiResponse error format.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": message,
            "meta": {"timestamp": datetime.now(timezone.utc).isoformat()},
        },
    )
