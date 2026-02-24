"""Redis 커넥션 풀 + 캐시 TTL 상수."""

from redis.asyncio import ConnectionPool, Redis

from src.backend.core.config import get_settings

settings = get_settings()

# 캐시 TTL 상수 (초 단위)
CACHE_TTL_DRUG_SEARCH = 60 * 60 * 24          # 24시간
CACHE_TTL_INTERACTION = 60 * 60 * 24 * 7      # 7일
CACHE_TTL_DRUG_DETAIL = 60 * 60 * 24 * 3      # 3일
CACHE_TTL_SUPPLEMENT_SEARCH = 60 * 60 * 24     # 24시간
CACHE_TTL_SUPPLEMENT_DETAIL = 60 * 60 * 24 * 3  # 3일
CACHE_TTL_AI_EXPLANATION = 60 * 60 * 24 * 30     # 30일

pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis() -> Redis:
    """Redis 클라이언트 인스턴스 반환."""
    return Redis(connection_pool=pool)
