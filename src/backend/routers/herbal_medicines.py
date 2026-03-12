"""한약재 라우터 — 한약재(생약) 검색 및 상세 조회."""

from fastapi import APIRouter, Depends, Path, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.herbal_medicine import (
    HerbalMedicineDetail,
    HerbalMedicineSearchItem,
)
from src.backend.services import herbal_medicine_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/herbal-medicines", tags=["herbal-medicines"])


@router.get(
    "/search",
    response_model=ApiResponse[PaginatedData[HerbalMedicineSearchItem]],
    summary="한약재 검색",
    description="한약재명, 한글명 등으로 한약재를 검색합니다.",
)
async def search_herbal_medicines(
    q: str = Query("", max_length=200, description="검색어 (한약재명, 한글명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """한약재 검색 엔드포인트.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[PaginatedData[HerbalMedicineSearchItem]] 포맷의 dict.
    """
    result = await herbal_medicine_service.search_herbal_medicines(
        db,
        redis,
        q,
        page,
        page_size,
    )
    return success_response(result)


@router.get(
    "/slugs",
    response_model=ApiResponse[list[str]],
    summary="한약재 slug 전체 목록",
    description="SSG generateStaticParams용 전체 slug 목록을 반환합니다.",
)
async def get_herbal_medicine_slugs(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """한약재 slug 전체 목록 엔드포인트."""
    slugs = await herbal_medicine_service.get_all_herbal_medicine_slugs(db, redis)
    return success_response(slugs)


@router.get(
    "/count",
    response_model=ApiResponse[int],
    summary="한약재 총 건수",
    description="전체 한약재 건수를 반환합니다.",
)
async def get_herbal_medicine_count(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """한약재 총 건수 엔드포인트."""
    count = await herbal_medicine_service.count_herbal_medicines(db, redis)
    return success_response(count)


@router.get(
    "/by-slug/{slug}",
    response_model=ApiResponse[HerbalMedicineDetail],
    summary="한약재 slug 조회",
    description="slug로 한약재 상세 정보를 조회합니다.",
)
async def get_herbal_medicine_by_slug(
    slug: str = Path(..., max_length=200, pattern=r"^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """한약재 slug 조회 엔드포인트."""
    result = await herbal_medicine_service.get_herbal_medicine_by_slug(db, redis, slug)
    if result is None:
        return error_response("한약재를 찾을 수 없습니다.", 404)
    return success_response(result)


@router.get(
    "/{herbal_id}",
    response_model=ApiResponse[HerbalMedicineDetail],
    summary="한약재 상세 조회",
    description="한약재 ID로 상세 정보를 조회합니다.",
)
async def get_herbal_medicine_detail(
    herbal_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """한약재 상세 조회 엔드포인트.

    Args:
        herbal_id: 조회할 한약재의 내부 ID.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[HerbalMedicineDetail] 포맷의 dict 또는 404 에러.
    """
    result = await herbal_medicine_service.get_herbal_medicine_detail(
        db,
        redis,
        herbal_id,
    )
    if result is None:
        return error_response("한약재를 찾을 수 없습니다.", 404)
    return success_response(result)
