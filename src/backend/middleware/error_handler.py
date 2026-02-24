"""글로벌 예외 처리 미들웨어 — 미처리 예외를 ApiResponse 포맷으로 반환."""

import logging
import traceback

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.backend.utils.response import error_response

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """모든 미처리 예외를 포착하여 ApiResponse 형식의 JSON으로 반환하는 미들웨어.

    - HTTPException: 원래 status_code를 유지하고 detail을 에러 메시지로 사용.
    - 그 외 예외: 500 Internal Server Error로 반환하고 상세 로그를 기록.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """요청을 처리하고, 예외 발생 시 표준 에러 응답을 반환한다.

        Args:
            request: 수신된 HTTP 요청.
            call_next: 다음 미들웨어/엔드포인트 호출 함수.

        Returns:
            Response 객체.
        """
        try:
            return await call_next(request)
        except HTTPException as exc:
            logger.warning(
                "HTTPException %d: %s — %s %s",
                exc.status_code,
                exc.detail,
                request.method,
                request.url.path,
            )
            return error_response(
                message=str(exc.detail),
                status_code=exc.status_code,
            )
        except Exception as exc:
            logger.error(
                "미처리 예외 발생: %s %s — %s\n%s",
                request.method,
                request.url.path,
                str(exc),
                traceback.format_exc(),
            )
            return error_response(
                message="서버 내부 오류가 발생했습니다.",
                status_code=500,
            )
