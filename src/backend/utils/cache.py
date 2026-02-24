"""Redis 캐시 유틸리티 — 키 생성, 해시, get/set 헬퍼."""

import hashlib
import json
import logging
from typing import Any

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


def make_cache_key(*parts: str) -> str:
    """캐시 키를 네임스페이스로 결합한다.

    Args:
        *parts: 키 구성 요소들.

    Returns:
        "yakmeogeo:part1:part2:..." 형식의 캐시 키.
    """
    return "yakmeogeo:" + ":".join(parts)


def hash_query(value: str) -> str:
    """검색어를 MD5 해시로 변환한다.

    Args:
        value: 해시할 문자열.

    Returns:
        MD5 해시의 앞 16자리 hex 문자열.
    """
    return hashlib.md5(value.encode()).hexdigest()[:16]


async def cache_get(redis: Redis, key: str) -> Any | None:
    """캐시에서 데이터를 조회한다.

    캐시 실패 시 경고 로그만 남기고 None을 반환한다 (서비스 중단 없음).

    Args:
        redis: Redis 클라이언트.
        key: 캐시 키.

    Returns:
        JSON 파싱된 데이터 또는 None.
    """
    try:
        raw = await redis.get(key)
        if raw is not None:
            return json.loads(raw)
    except Exception:
        logger.warning("캐시 조회 실패: key=%s", key, exc_info=True)
    return None


async def cache_set(redis: Redis, key: str, data: Any, ttl: int) -> None:
    """캐시에 데이터를 저장한다.

    캐시 실패 시 경고 로그만 남기고 무시한다 (서비스 중단 없음).

    Args:
        redis: Redis 클라이언트.
        key: 캐시 키.
        data: 저장할 데이터 (JSON 직렬화 가능해야 함).
        ttl: TTL(초 단위).
    """
    try:
        await redis.set(key, json.dumps(data, ensure_ascii=False, default=str), ex=ttl)
    except Exception:
        logger.warning("캐시 저장 실패: key=%s", key, exc_info=True)
