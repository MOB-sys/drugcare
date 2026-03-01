"""약먹어 FastAPI 애플리케이션 — 메인 엔트리포인트."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.core.config import get_settings
from src.backend.core.database import engine
from src.backend.core.redis import pool as redis_pool
from src.backend.middleware.device_auth import DeviceAuthMiddleware
from src.backend.middleware.error_handler import ErrorHandlerMiddleware
from src.backend.middleware.rate_limiter import RateLimiterMiddleware
from src.backend.middleware.request_logger import RequestLoggerMiddleware
from src.backend.middleware.security_headers import SecurityHeadersMiddleware
from src.backend.routers import (
    cabinet,
    drugs,
    feedback,
    health,
    interactions,
    metrics,
    reminders,
    supplements,
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """애플리케이션 수명주기 관리.

    - startup: 로깅 초기화 및 서비스 시작 로그.
    - shutdown: DB 엔진 dispose 및 Redis 커넥션 풀 종료.

    Args:
        app: FastAPI 애플리케이션 인스턴스.
    """
    # Startup
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info(
        "약먹어 API 서버 시작 — 환경: %s, 디버그: %s",
        settings.APP_ENV,
        settings.DEBUG,
    )

    yield

    # Shutdown
    logger.info("약먹어 API 서버 종료 중...")
    await engine.dispose()
    logger.info("DB 엔진 dispose 완료")
    await redis_pool.disconnect()
    logger.info("Redis 커넥션 풀 종료 완료")


app = FastAPI(
    title="약먹어 API",
    version="0.1.0",
    description="약물/영양제 상호작용 체커 및 복약 관리 서비스",
    lifespan=lifespan,
)

# --- 미들웨어 등록 (역순으로 실행됨: 마지막에 추가한 것이 가장 먼저 실행) ---
# 실행 순서: ErrorHandler → RequestLogger → SecurityHeaders → RateLimiter → DeviceAuth → CORS

# CORS 미들웨어 (가장 안쪽)
_cors_origins = (
    ["*"]
    if settings.is_development
    else [
        "https://pillright.com",
        "https://www.pillright.com",
        "https://api.pillright.com",
        "http://localhost:3000",
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 디바이스 인증 미들웨어
app.add_middleware(DeviceAuthMiddleware)

# 레이트 리미터 미들웨어
app.add_middleware(RateLimiterMiddleware)

# 보안 헤더 미들웨어
app.add_middleware(SecurityHeadersMiddleware)

# 요청 로깅 미들웨어
app.add_middleware(RequestLoggerMiddleware)

# 글로벌 에러 핸들러 미들웨어 (가장 바깥에서 예외를 잡도록 마지막 등록)
app.add_middleware(ErrorHandlerMiddleware)

# --- 라우터 등록 ---
api_prefix = settings.API_V1_PREFIX

# 헬스체크는 /api/v1/health
app.include_router(health.router, prefix=api_prefix)

# 기능별 라우터
app.include_router(drugs.router, prefix=api_prefix)
app.include_router(supplements.router, prefix=api_prefix)
app.include_router(interactions.router, prefix=api_prefix)
app.include_router(cabinet.router, prefix=api_prefix)
app.include_router(reminders.router, prefix=api_prefix)
app.include_router(feedback.router, prefix=api_prefix)
app.include_router(metrics.router, prefix=api_prefix)
