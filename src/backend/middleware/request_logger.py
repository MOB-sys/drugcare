"""요청 로깅 미들웨어 — 요청별 UUID 부여 및 구조화된 로그 기록."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """요청마다 고유 UUID를 생성하고 구조화된 로그를 기록하는 미들웨어.

    - 요청 시작 시 UUID를 생성하여 request.state.request_id에 저장.
    - 응답 헤더에 X-Request-ID를 추가.
    - 메서드, 경로, 상태 코드, 처리 시간(ms)을 로그에 기록.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """요청을 로깅하고 X-Request-ID 헤더를 추가한다.

        Args:
            request: 수신된 HTTP 요청.
            call_next: 다음 미들웨어/엔드포인트 호출 함수.

        Returns:
            X-Request-ID 헤더가 추가된 Response 객체.
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "method=%s path=%s status=%d duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
