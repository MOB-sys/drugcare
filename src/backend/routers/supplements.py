"""영양제 라우터 — 건강기능식품 검색 및 상세 조회."""

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.supplement import SupplementDetail, SupplementSearchItem
from src.backend.services import supplement_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/supplements", tags=["supplements"])


@router.get(
    "/search",
    response_model=ApiResponse[PaginatedData[SupplementSearchItem]],
    summary="영양제 검색",
    description="제품명, 성분명 등으로 건강기능식품을 검색합니다.",
)
async def search_supplements(
    q: str = Query("", description="검색어 (제품명, 성분명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """건강기능식품 검색 엔드포인트.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[PaginatedData[SupplementSearchItem]] 포맷의 dict.
    """
    result = await supplement_service.search_supplements(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/slugs",
    response_model=ApiResponse[list[str]],
    summary="영양제 slug 전체 목록",
    description="SSG generateStaticParams용 전체 slug 목록을 반환합니다.",
)
async def get_supplement_slugs(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """영양제 slug 전체 목록 엔드포인트."""
    slugs = await supplement_service.get_all_supplement_slugs(db, redis)
    return success_response(slugs)


@router.get(
    "/count",
    response_model=ApiResponse[int],
    summary="영양제 총 건수",
    description="전체 영양제 건수를 반환합니다.",
)
async def get_supplement_count(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """영양제 총 건수 엔드포인트."""
    count = await supplement_service.count_supplements(db, redis)
    return success_response(count)


@router.get(
    "/by-slug/{slug}",
    response_model=ApiResponse[SupplementDetail],
    summary="영양제 slug 조회",
    description="slug로 영양제 상세 정보를 조회합니다.",
)
async def get_supplement_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """영양제 slug 조회 엔드포인트."""
    result = await supplement_service.get_supplement_by_slug(db, redis, slug)
    if result is None:
        return error_response("영양제를 찾을 수 없습니다.", 404)
    return success_response(result)


@router.get(
    "/{supplement_id}",
    response_model=ApiResponse[SupplementDetail],
    summary="영양제 상세 조회",
    description="영양제 ID로 상세 정보를 조회합니다.",
)
async def get_supplement_detail(
    supplement_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """영양제 상세 조회 엔드포인트.

    Args:
        supplement_id: 조회할 영양제의 내부 ID.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[SupplementDetail] 포맷의 dict 또는 404 에러.
    """
    result = await supplement_service.get_supplement_detail(db, redis, supplement_id)
    if result is None:
        return error_response("영양제를 찾을 수 없습니다.", 404)
    return success_response(result)
