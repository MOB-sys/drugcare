"""리뷰 라우터 — 약물/영양제 리뷰 CRUD."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.review import ReviewCreate, ReviewResponse, ReviewSummary
from src.backend.services import review_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=ApiResponse[ReviewResponse],
    summary="리뷰 작성",
    description="약물/영양제에 대한 리뷰를 작성하거나 수정합니다.",
)
async def create_review(
    item_type: str = Query(..., description="항목 유형 (drug/supplement)"),
    item_id: int = Query(..., description="항목 ID"),
    body: ReviewCreate = ...,
    request: Request = ...,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """리뷰 작성/수정 엔드포인트.

    Args:
        item_type: 'drug' 또는 'supplement'.
        item_id: 약물/영양제 ID.
        body: 리뷰 데이터.
        request: HTTP 요청 (device_id 추출용).
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[ReviewResponse] 포맷의 dict.
    """
    if item_type not in ("drug", "supplement"):
        return error_response("item_type은 'drug' 또는 'supplement'이어야 합니다.", status_code=422)

    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise HTTPException(status_code=401, detail="Device ID is required")
    result = await review_service.create_review(db, redis, device_id, item_type, item_id, body)
    return success_response(result)


@router.get(
    "/{item_type}/{item_id}",
    response_model=ApiResponse[PaginatedData[ReviewResponse]],
    summary="리뷰 목록",
    description="약물/영양제의 리뷰 목록을 페이지네이션으로 조회합니다.",
)
async def get_reviews(
    item_type: str,
    item_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, ge=1, le=50, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """리뷰 목록 엔드포인트."""
    if item_type not in ("drug", "supplement"):
        return error_response("item_type은 'drug' 또는 'supplement'이어야 합니다.", status_code=422)

    result = await review_service.get_reviews(db, redis, item_type, item_id, page, page_size)
    return success_response(result)


@router.get(
    "/{item_type}/{item_id}/summary",
    response_model=ApiResponse[ReviewSummary],
    summary="리뷰 요약",
    description="약물/영양제의 리뷰 요약 통계를 조회합니다.",
)
async def get_review_summary(
    item_type: str,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """리뷰 요약 엔드포인트."""
    if item_type not in ("drug", "supplement"):
        return error_response("item_type은 'drug' 또는 'supplement'이어야 합니다.", status_code=422)

    result = await review_service.get_review_summary(db, redis, item_type, item_id)
    return success_response(result)


@router.post(
    "/{review_id}/helpful",
    response_model=ApiResponse[ReviewResponse],
    summary="도움됨 표시",
    description="리뷰에 도움됨 표시를 합니다.",
)
async def mark_helpful(
    review_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """도움됨 표시 엔드포인트."""
    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise HTTPException(status_code=401, detail="Device ID is required")
    result = await review_service.mark_helpful(db, redis, review_id)
    if result is None:
        return error_response("리뷰를 찾을 수 없습니다.", 404)
    return success_response(result)


@router.delete(
    "/{review_id}",
    response_model=ApiResponse[bool],
    summary="리뷰 삭제",
    description="자신의 리뷰를 삭제합니다.",
)
async def delete_review(
    review_id: int,
    request: Request = ...,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """리뷰 삭제 엔드포인트."""
    device_id = getattr(request.state, "device_id", None)
    if not device_id:
        raise HTTPException(status_code=401, detail="Device ID is required")
    deleted = await review_service.delete_review(db, redis, device_id, review_id)
    if not deleted:
        return error_response("리뷰를 찾을 수 없거나 삭제 권한이 없습니다.", 404)
    return success_response(True)
