"""디바이스 인증 미들웨어 — X-Device-ID 헤더 + 웹 세션쿠키 검증."""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.backend.utils.response import error_response

logger = logging.getLogger(__name__)

# 인증 면제 경로 목록 (exact match)
EXEMPT_PATHS: set[str] = {
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# 인증 면제 경로 접두사 (SSG 빌드용 공개 API)
EXEMPT_PREFIXES: tuple[str, ...] = (
    "/api/v1/drugs/slugs",
    "/api/v1/drugs/count",
    "/api/v1/drugs/by-slug/",
    "/api/v1/supplements/slugs",
    "/api/v1/supplements/count",
    "/api/v1/supplements/by-slug/",
)


class DeviceAuthMiddleware(BaseHTTPMiddleware):
    """X-Device-ID 헤더 또는 웹 세션쿠키를 검증하는 인증 미들웨어.

    - 면제 경로(EXEMPT_PATHS, EXEMPT_PREFIXES)는 인증 없이 통과.
    - X-Device-ID 헤더가 있으면 앱 클라이언트로 처리.
    - 헤더 없으면 session_id 쿠키를 확인 (웹 클라이언트).
    - 둘 다 없으면 web-{uuid4} 생성 후 Set-Cookie.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """요청의 디바이스 인증을 확인하고 처리한다."""
        path = request.url.path

        # 면제 경로 확인 (exact match)
        if path in EXEMPT_PATHS:
            return await call_next(request)

        # 면제 경로 확인 (prefix match)
        if path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        # 1) X-Device-ID 헤더 (앱 클라이언트)
        device_id = request.headers.get("X-Device-ID")
        if device_id:
            request.state.device_id = device_id
            return await call_next(request)

        # 2) session_id 쿠키 (웹 클라이언트)
        session_id = request.cookies.get("session_id")
        if session_id:
            request.state.device_id = session_id
            return await call_next(request)

        # 3) 둘 다 없으면 새 웹 세션 생성
        new_session_id = f"web-{uuid4()}"
        request.state.device_id = new_session_id
        response = await call_next(request)
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            max_age=60 * 60 * 24 * 365,
            httponly=True,
            samesite="lax",
        )
        return response


def uuid4() -> str:
    """UUID4 문자열을 생성한다."""
    return str(uuid.uuid4())
