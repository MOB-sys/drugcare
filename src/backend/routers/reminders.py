"""리마인더 라우터 — 복약 알림 스케줄 관리 (스텁)."""

from fastapi import APIRouter, Request

from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post(
    "",
    response_model=ApiResponse[dict],
    summary="리마인더 생성",
    description="복약 리마인더를 생성합니다.",
)
async def create_reminder(
    request: Request,
) -> dict:
    """리마인더 생성 엔드포인트 (스텁).

    Phase 2에서 실제 DB 저장 및 알림 스케줄링으로 구현 예정.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        ApiResponse 포맷의 dict.
    """
    device_id = request.state.device_id
    return success_response({
        "message": "리마인더 생성 구현 예정입니다.",
        "device_id": device_id,
    })


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[dict]],
    summary="리마인더 목록 조회",
    description="사용자의 리마인더 목록을 조회합니다.",
)
async def list_reminders(
    request: Request,
) -> dict:
    """리마인더 목록 조회 엔드포인트 (스텁).

    request.state.device_id로 사용자를 식별한다.
    Phase 2에서 실제 DB 조회로 구현 예정.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        ApiResponse[PaginatedData] 포맷의 dict.
    """
    _device_id = request.state.device_id
    paginated = PaginatedData[dict](
        items=[],
        total=0,
        page=1,
        page_size=20,
        total_pages=0,
    )
    return success_response(paginated.model_dump())


@router.patch(
    "/{reminder_id}",
    response_model=ApiResponse[dict],
    summary="리마인더 수정",
    description="기존 리마인더의 설정을 변경합니다.",
)
async def update_reminder(
    reminder_id: int,
    request: Request,
) -> dict:
    """리마인더 수정 엔드포인트 (스텁).

    Phase 2에서 실제 DB 업데이트로 구현 예정.

    Args:
        reminder_id: 수정할 리마인더의 내부 ID.
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        404 에러 응답 (구현 예정).
    """
    _device_id = request.state.device_id
    return error_response(
        message=f"리마인더 수정 구현 예정입니다. (reminder_id={reminder_id})",
        status_code=404,
    )


@router.delete(
    "/{reminder_id}",
    response_model=ApiResponse[dict],
    summary="리마인더 삭제",
    description="리마인더를 삭제합니다.",
)
async def delete_reminder(
    reminder_id: int,
    request: Request,
) -> dict:
    """리마인더 삭제 엔드포인트 (스텁).

    Phase 2에서 실제 DB 삭제로 구현 예정.

    Args:
        reminder_id: 삭제할 리마인더의 내부 ID.
        request: HTTP 요청 (device_id는 request.state에서 추출).

    Returns:
        404 에러 응답 (구현 예정).
    """
    _device_id = request.state.device_id
    return error_response(
        message=f"리마인더 삭제 구현 예정입니다. (reminder_id={reminder_id})",
        status_code=404,
    )
