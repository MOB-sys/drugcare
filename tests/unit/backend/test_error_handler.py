"""ErrorHandlerMiddleware 단위 테스트 — HTTPException/일반 예외 처리 검증."""

import json
import logging
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from src.backend.middleware.error_handler import ErrorHandlerMiddleware


# ---------------------------------------------------------------------------
# dispatch 직접 테스트용 헬퍼
# ---------------------------------------------------------------------------


def _make_request(method: str = "GET", path: str = "/test") -> MagicMock:
    """테스트용 모의 Request 객체를 생성한다."""
    req = MagicMock(spec=Request)
    req.method = method
    req.url = MagicMock()
    req.url.path = path
    return req


def _make_middleware() -> ErrorHandlerMiddleware:
    """테스트용 ErrorHandlerMiddleware 인스턴스를 생성한다."""
    app = MagicMock()
    return ErrorHandlerMiddleware(app)


# ---------------------------------------------------------------------------
# 테스트용 미니 FastAPI 앱 — 일반 예외 엔드포인트
# ---------------------------------------------------------------------------

_test_app = FastAPI()
_test_app.add_middleware(ErrorHandlerMiddleware)


@_test_app.get("/ok")
async def _route_ok():
    """정상 응답."""
    return {"message": "ok"}


@_test_app.get("/unexpected")
async def _route_unexpected():
    """예상치 못한 일반 예외."""
    raise RuntimeError("DB 연결 실패")


@pytest_asyncio.fixture
async def error_client():
    """ErrorHandlerMiddleware가 적용된 테스트 클라이언트를 생성한다."""
    transport = httpx.ASGITransport(app=_test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# 정상 요청 통과
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_normal_request_passes_through(error_client: httpx.AsyncClient):
    """예외가 없으면 미들웨어가 응답을 그대로 통과시킨다."""
    resp = await error_client.get("/ok")
    assert resp.status_code == 200
    assert resp.json()["message"] == "ok"


# ---------------------------------------------------------------------------
# HTTPException 처리 — dispatch 직접 테스트
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_http_exception_preserves_status_code():
    """HTTPException의 status_code가 응답에 그대로 유지된다."""
    middleware = _make_middleware()
    request = _make_request()
    call_next = AsyncMock(side_effect=HTTPException(status_code=404, detail="리소스를 찾을 수 없습니다."))

    resp = await middleware.dispatch(request, call_next)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_http_exception_response_format():
    """HTTPException 발생 시 ApiResponse 표준 에러 포맷을 반환한다."""
    middleware = _make_middleware()
    request = _make_request()
    call_next = AsyncMock(side_effect=HTTPException(status_code=404, detail="리소스를 찾을 수 없습니다."))

    resp = await middleware.dispatch(request, call_next)
    body = json.loads(resp.body.decode("utf-8"))

    assert body["success"] is False
    assert body["data"] is None
    assert body["error"] == "리소스를 찾을 수 없습니다."
    assert "timestamp" in body["meta"]


@pytest.mark.asyncio
async def test_http_exception_422_status():
    """HTTPException 422 상태 코드도 올바르게 전달된다."""
    middleware = _make_middleware()
    request = _make_request()
    call_next = AsyncMock(side_effect=HTTPException(status_code=422, detail="유효하지 않은 요청입니다."))

    resp = await middleware.dispatch(request, call_next)
    assert resp.status_code == 422

    body = json.loads(resp.body.decode("utf-8"))
    assert body["error"] == "유효하지 않은 요청입니다."


@pytest.mark.asyncio
async def test_http_exception_logs_warning(caplog):
    """HTTPException 발생 시 logger.warning이 호출된다."""
    middleware = _make_middleware()
    request = _make_request(path="/api/test")
    call_next = AsyncMock(side_effect=HTTPException(status_code=404, detail="not found"))

    with caplog.at_level(logging.WARNING, logger="src.backend.middleware.error_handler"):
        await middleware.dispatch(request, call_next)

    assert any("HTTPException 404" in msg for msg in caplog.messages)


# ---------------------------------------------------------------------------
# 일반 예외 → 500 처리
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500(error_client: httpx.AsyncClient):
    """일반 예외 발생 시 500 상태 코드를 반환한다."""
    resp = await error_client.get("/unexpected")
    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_unhandled_exception_generic_message(error_client: httpx.AsyncClient):
    """일반 예외 시 내부 정보를 숨기고 일반적인 에러 메시지를 반환한다."""
    resp = await error_client.get("/unexpected")
    body = resp.json()

    assert body["success"] is False
    assert body["error"] == "서버 내부 오류가 발생했습니다."
    assert "DB 연결 실패" not in body["error"]


@pytest.mark.asyncio
async def test_unhandled_exception_response_format():
    """일반 예외 발생 시 ApiResponse 표준 에러 포맷을 반환한다."""
    middleware = _make_middleware()
    request = _make_request()
    call_next = AsyncMock(side_effect=RuntimeError("unexpected"))

    resp = await middleware.dispatch(request, call_next)
    body = json.loads(resp.body.decode("utf-8"))

    assert body["success"] is False
    assert body["data"] is None
    assert body["error"] == "서버 내부 오류가 발생했습니다."
    assert "timestamp" in body["meta"]


@pytest.mark.asyncio
async def test_unhandled_exception_logs_error(caplog):
    """일반 예외 발생 시 logger.error가 호출된다."""
    middleware = _make_middleware()
    request = _make_request(path="/api/fail")
    call_next = AsyncMock(side_effect=ValueError("boom"))

    with caplog.at_level(logging.ERROR, logger="src.backend.middleware.error_handler"):
        await middleware.dispatch(request, call_next)

    assert any("미처리 예외 발생" in msg for msg in caplog.messages)
