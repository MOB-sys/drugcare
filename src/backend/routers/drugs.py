"""의약품 라우터 — 약물 검색 및 상세 조회."""

from fastapi import APIRouter, Depends, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.drug import DrugDetail, DrugSearchItem
from src.backend.services import drug_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get(
    "/search",
    response_model=ApiResponse[PaginatedData[DrugSearchItem]],
    summary="의약품 검색",
    description="제품명, 성분명 등으로 의약품을 검색합니다.",
)
async def search_drugs(
    q: str = Query("", description="검색어 (제품명, 성분명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=5000, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 검색 엔드포인트.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[PaginatedData[DrugSearchItem]] 포맷의 dict.
    """
    result = await drug_service.search_drugs(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/slugs",
    response_model=ApiResponse[list[str]],
    summary="의약품 slug 전체 목록",
    description="SSG generateStaticParams용 전체 slug 목록을 반환합니다.",
)
async def get_drug_slugs(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 slug 전체 목록 엔드포인트."""
    slugs = await drug_service.get_all_drug_slugs(db, redis)
    return success_response(slugs)


@router.get(
    "/count",
    response_model=ApiResponse[int],
    summary="의약품 총 건수",
    description="전체 의약품 건수를 반환합니다.",
)
async def get_drug_count(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 총 건수 엔드포인트."""
    count = await drug_service.count_drugs(db, redis)
    return success_response(count)


@router.get(
    "/by-slug/{slug}",
    response_model=ApiResponse[DrugDetail],
    summary="의약품 slug 조회",
    description="slug로 의약품 상세 정보를 조회합니다.",
)
async def get_drug_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 slug 조회 엔드포인트."""
    result = await drug_service.get_drug_by_slug(db, redis, slug)
    if result is None:
        return error_response("의약품을 찾을 수 없습니다.", 404)
    return success_response(result)


@router.get(
    "/{drug_id}",
    response_model=ApiResponse[DrugDetail],
    summary="의약품 상세 조회",
    description="의약품 ID로 상세 정보를 조회합니다.",
)
async def get_drug_detail(
    drug_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 상세 조회 엔드포인트.

    Args:
        drug_id: 조회할 의약품의 내부 ID.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[DrugDetail] 포맷의 dict 또는 404 에러.
    """
    result = await drug_service.get_drug_detail(db, redis, drug_id)
    if result is None:
        return error_response("의약품을 찾을 수 없습니다.", 404)
    return success_response(result)
