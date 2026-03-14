"""디바이스 인증 미들웨어 — X-Device-ID 헤더 + 웹 세션쿠키 검증."""

import logging
import re
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

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
    "/api/v1/drugs/recent",
    "/api/v1/drugs/symptoms/search",
    "/api/v1/supplements/slugs",
    "/api/v1/supplements/count",
    "/api/v1/supplements/by-slug/",
    "/api/v1/reviews/drug/",
    "/api/v1/reviews/supplement/",
)


class DeviceAuthMiddleware(BaseHTTPMiddleware):
    """X-Device-ID 헤더 또는 웹 세션쿠키를 검증하는 인증 미들웨어.

    - 면제 경로(EXEMPT_PATHS, EXEMPT_PREFIXES)는 인증 없이 통과.
    - X-Device-ID 헤더가 있으면 앱 클라이언트로 처리.
    - 헤더 없으면 session_id 쿠키를 확인 (웹 클라이언트).
    - 둘 다 없으면 web-{uuid4} 생성 후 Set-Cookie.
    - 모든 상태 변경 요청(POST/PUT/PATCH/DELETE)은 Origin/Referer 검증 필수.
    """

    # CSRF 허용 Origin 목록 (클래스 레벨 상수)
    _ALLOWED_ORIGINS: set[str] = {
        "https://pillright.com",
        "https://www.pillright.com",
        "http://localhost:3000",
    }

    def _check_csrf(self, request: Request) -> bool:
        """상태 변경 요청의 Origin/Referer를 검증한다.

        Args:
            request: HTTP 요청 객체.

        Returns:
            True이면 통과, False이면 CSRF 차단.
        """
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return True

        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        # Origin 또는 Referer 중 하나라도 허용 목록과 일치하면 통과
        if any(origin.startswith(o) or referer.startswith(o) for o in self._ALLOWED_ORIGINS):
            return True

        # 네이티브 앱: Origin/Referer가 둘 다 비어있고 X-Device-ID가 있으면 통과
        return bool(not origin and not referer and request.headers.get("X-Device-ID"))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """요청의 디바이스 인증을 확인하고 처리한다."""
        path = request.url.path

        # 면제 경로 확인 (exact match)
        if path in EXEMPT_PATHS:
            return await call_next(request)

        # 면제 경로 확인 (prefix match)
        if path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        # CSRF 보호: 모든 상태 변경 요청에 대해 Origin/Referer 검증
        if not self._check_csrf(request):
            from starlette.responses import JSONResponse

            return JSONResponse(
                {"success": False, "error": "CSRF 검증 실패"},
                status_code=403,
            )

        # 1) X-Device-ID 헤더 (앱 클라이언트)
        device_id = request.headers.get("X-Device-ID")
        if device_id and _UUID_RE.match(device_id):
            request.state.device_id = device_id
            return await call_next(request)

        # 2) session_id 쿠키 (웹 클라이언트)
        session_id = request.cookies.get("session_id")
        if session_id and session_id.startswith("web-") and _UUID_RE.match(session_id[4:]):
            request.state.device_id = session_id
            return await call_next(request)

        # 3) 둘 다 없으면 새 웹 세션 생성
        new_session_id = f"web-{uuid4()}"
        request.state.device_id = new_session_id
        response = await call_next(request)
        response.set_cookie(
            key="session_id",
            value=new_session_id,
            max_age=60 * 60 * 24 * 90,
            httponly=True,
            samesite="strict",
            secure=True,
        )
        return response


def uuid4() -> str:
    """UUID4 문자열을 생성한다."""
    return str(uuid.uuid4())
