"""레이트 리미터 미들웨어 — Redis 기반 슬라이딩 윈도우 요청 제한."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.backend.core.redis import get_redis
from src.backend.utils.response import error_response

logger = logging.getLogger(__name__)

# 레이트 리밋 면제 경로
EXEMPT_PATHS: set[str] = {
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# 엔드포인트 그룹별 요청 제한 (req/min)
RATE_LIMITS: dict[str, int] = {
    "search": 60,
    "mutation": 30,
}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Redis 기반 슬라이딩 윈도우 레이트 리미터.

    - search (GET 요청): 분당 60회 제한.
    - mutation (POST/PATCH/DELETE 요청): 분당 30회 제한.
    - Redis 장애 시 요청을 통과시킨다 (graceful degradation).
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """요청의 레이트 리밋을 확인하고 처리한다.

        Args:
            request: 수신된 HTTP 요청.
            call_next: 다음 미들웨어/엔드포인트 호출 함수.

        Returns:
            Response 객체. 제한 초과 시 429 응답.
        """
        path = request.url.path

        if path in EXEMPT_PATHS:
            return await call_next(request)

        group = _get_endpoint_group(request.method)
        limit = RATE_LIMITS.get(group, 60)
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}:{group}"

        try:
            redis = get_redis()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, 60)
            if count > limit:
                return error_response(
                    message="요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
                    status_code=429,
                )
        except Exception:
            logger.warning("Redis 연결 실패 — 레이트 리밋 검사를 건너뜁니다: %s", key)

        return await call_next(request)


def _get_endpoint_group(method: str) -> str:
    """HTTP 메서드를 엔드포인트 그룹으로 매핑한다.

    Args:
        method: HTTP 메서드 (GET, POST 등).

    Returns:
        엔드포인트 그룹명 ("search" 또는 "mutation").
    """
    if method in ("POST", "PATCH", "DELETE"):
        return "mutation"
    return "search"
