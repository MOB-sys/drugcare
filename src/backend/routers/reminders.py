"""리마인더 라우터 — 복약 알림 스케줄 관리."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.schemas.common import ApiResponse
from src.backend.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate
from src.backend.services import reminder_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post(
    "",
    response_model=ApiResponse[ReminderResponse],
    summary="리마인더 생성",
    description="복약 리마인더를 생성합니다.",
)
async def create_reminder(
    data: ReminderCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """리마인더 생성 엔드포인트.

    Args:
        data: 리마인더 생성 정보.
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[ReminderResponse] 포맷의 dict.
    """
    device_id = request.state.device_id
    result = await reminder_service.create_reminder(db, device_id, data)

    if result is None:
        return error_response("복약함 아이템을 찾을 수 없습니다.", 404)

    return success_response(result)


@router.get(
    "",
    response_model=ApiResponse[list[ReminderResponse]],
    summary="리마인더 목록 조회",
    description="사용자의 리마인더 목록을 조회합니다.",
)
async def list_reminders(
    request: Request,
    active_only: bool = Query(True, description="활성 리마인더만 조회"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """리마인더 목록 조회 엔드포인트.

    Args:
        request: HTTP 요청 (device_id는 request.state에서 추출).
        active_only: True이면 활성 리마인더만 조회.
        db: DB 세션 (DI).

    Returns:
        ApiResponse[list[ReminderResponse]] 포맷의 dict.
    """
    device_id = request.state.device_id
    items = await reminder_service.list_reminders(db, device_id, active_only)
    return success_response(items)


@router.patch(
    "/{reminder_id}",
    response_model=ApiResponse[ReminderResponse],
    summary="리마인더 수정",
    description="기존 리마인더의 설정을 변경합니다.",
)
async def update_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """리마인더 수정 엔드포인트.

    Args:
        reminder_id: 수정할 리마인더의 내부 ID.
        data: 수정 정보 (설정된 필드만 반영).
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse[ReminderResponse] 포맷의 dict 또는 404 에러.
    """
    device_id = request.state.device_id
    result = await reminder_service.update_reminder(db, device_id, reminder_id, data)

    if result is None:
        return error_response("리마인더를 찾을 수 없습니다.", 404)

    return success_response(result)


@router.delete(
    "/{reminder_id}",
    response_model=ApiResponse[dict],
    summary="리마인더 삭제",
    description="리마인더를 삭제합니다.",
)
async def delete_reminder(
    reminder_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """리마인더 삭제 엔드포인트.

    Args:
        reminder_id: 삭제할 리마인더의 내부 ID.
        request: HTTP 요청 (device_id는 request.state에서 추출).
        db: DB 세션 (DI).

    Returns:
        ApiResponse 포맷의 dict 또는 404 에러.
    """
    device_id = request.state.device_id
    result = await reminder_service.delete_reminder(db, device_id, reminder_id)

    if result is None:
        return error_response("리마인더를 찾을 수 없습니다.", 404)

    return success_response({"message": "리마인더가 삭제되었습니다."})
