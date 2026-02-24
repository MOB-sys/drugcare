"""헬스체크 엔드포인트 테스트."""

import pytest


@pytest.mark.asyncio
async def test_health_check_success(client):
    """정상 상태에서 헬스체크가 healthy를 반환하는지 확인한다."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["error"] is None
    assert body["data"]["status"] == "healthy"
    assert body["data"]["database"] == "ok"
    assert body["data"]["redis"] == "ok"
    assert "timestamp" in body["meta"]


@pytest.mark.asyncio
async def test_health_check_db_failure(client_db_error):
    """DB 연결 실패 시 degraded 상태와 database=error를 반환하는지 확인한다."""
    response = await client_db_error.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "degraded"
    assert body["data"]["database"] == "error"
    assert body["data"]["redis"] == "ok"


@pytest.mark.asyncio
async def test_health_check_redis_failure(client_redis_error):
    """Redis 연결 실패 시 degraded 상태와 redis=error를 반환하는지 확인한다."""
    response = await client_redis_error.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "degraded"
    assert body["data"]["database"] == "ok"
    assert body["data"]["redis"] == "error"
