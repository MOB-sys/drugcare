"""Redis 캐시 유틸리티 단위 테스트 — 키 생성, 해시, get/set 헬퍼."""

import json
from unittest.mock import AsyncMock

import pytest

from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key


# ---------------------------------------------------------------------------
# make_cache_key
# ---------------------------------------------------------------------------


def test_make_cache_key_single_part():
    """단일 파트로 네임스페이스 키를 생성한다."""
    assert make_cache_key("drug") == "yakmeogeo:drug"


def test_make_cache_key_multiple_parts():
    """복수 파트를 콜론으로 결합한 키를 생성한다."""
    assert make_cache_key("drug", "search", "abc") == "yakmeogeo:drug:search:abc"


def test_make_cache_key_empty():
    """파트 없이 호출 시 네임스페이스만 반환한다."""
    assert make_cache_key() == "yakmeogeo:"


# ---------------------------------------------------------------------------
# hash_query
# ---------------------------------------------------------------------------


def test_hash_query_deterministic():
    """동일 입력에 대해 항상 동일한 해시를 반환한다."""
    assert hash_query("타이레놀") == hash_query("타이레놀")


def test_hash_query_length():
    """해시 결과는 정확히 16자리이다."""
    assert len(hash_query("test")) == 16


def test_hash_query_uniqueness():
    """서로 다른 입력은 서로 다른 해시를 반환한다."""
    assert hash_query("타이레놀") != hash_query("아스피린")


def test_hash_query_hex_format():
    """해시 결과는 16진수 문자열이다."""
    result = hash_query("vitamin_c")
    assert all(c in "0123456789abcdef" for c in result)


# ---------------------------------------------------------------------------
# cache_get
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_get_returns_parsed_json():
    """캐시 히트 시 JSON 파싱된 데이터를 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"key": "value"})

    result = await cache_get(mock_redis, "yakmeogeo:test")
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_cache_get_miss_returns_none():
    """캐시 미스 시 None을 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    result = await cache_get(mock_redis, "yakmeogeo:missing")
    assert result is None


@pytest.mark.asyncio
async def test_cache_get_redis_error_returns_none():
    """Redis 장애 시 예외를 전파하지 않고 None을 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.get.side_effect = ConnectionError("Redis down")

    result = await cache_get(mock_redis, "yakmeogeo:fail")
    assert result is None


@pytest.mark.asyncio
async def test_cache_get_invalid_json_returns_none():
    """유효하지 않은 JSON 데이터는 None을 반환한다."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "not-valid-json{{"

    result = await cache_get(mock_redis, "yakmeogeo:bad")
    assert result is None


# ---------------------------------------------------------------------------
# cache_set
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_set_serializes_and_sets_ttl():
    """데이터를 JSON 직렬화하고 TTL과 함께 저장한다."""
    mock_redis = AsyncMock()
    data = {"interactions_found": 3}

    await cache_set(mock_redis, "yakmeogeo:test", data, ttl=300)

    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    stored_json = call_args[0][1]
    assert json.loads(stored_json) == data
    assert call_args[1]["ex"] == 300


@pytest.mark.asyncio
async def test_cache_set_ensure_ascii_false():
    """한글 데이터가 이스케이프 없이 그대로 저장된다."""
    mock_redis = AsyncMock()
    data = {"name": "타이레놀"}

    await cache_set(mock_redis, "yakmeogeo:kr", data, ttl=60)

    stored_json = mock_redis.set.call_args[0][1]
    assert "타이레놀" in stored_json


@pytest.mark.asyncio
async def test_cache_set_redis_error_no_propagation():
    """Redis 장애 시 예외를 전파하지 않는다 (서비스 중단 없음)."""
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = ConnectionError("Redis down")

    # 예외가 전파되지 않아야 한다
    await cache_set(mock_redis, "yakmeogeo:fail", {"a": 1}, ttl=60)
