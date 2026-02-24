"""디바이스 인증 미들웨어 — X-Device-ID 헤더 검증."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.backend.utils.response import error_response

logger = logging.getLogger(__name__)

# 인증 면제 경로 목록
EXEMPT_PATHS: set[str] = {
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class DeviceAuthMiddleware(BaseHTTPMiddleware):
    """X-Device-ID 헤더를 검증하는 인증 미들웨어.

    - 면제 경로(EXEMPT_PATHS)는 헤더 없이도 통과.
    - 그 외 경로는 X-Device-ID 헤더가 없으면 401 응답.
    - 헤더가 있으면 request.state.device_id에 저장.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """요청의 X-Device-ID 헤더를 확인하고 처리한다.

        Args:
            request: 수신된 HTTP 요청.
            call_next: 다음 미들웨어/엔드포인트 호출 함수.

        Returns:
            Response 객체.
        """
        path = request.url.path

        # 면제 경로 확인
        if path in EXEMPT_PATHS:
            return await call_next(request)

        # X-Device-ID 헤더 추출
        device_id = request.headers.get("X-Device-ID")

        if not device_id:
            logger.warning("요청에 X-Device-ID 헤더 누락: %s %s", request.method, path)
            return error_response(
                message="X-Device-ID 헤더가 필요합니다.",
                status_code=401,
            )

        # 디바이스 ID를 request.state에 저장
        request.state.device_id = device_id
        return await call_next(request)
