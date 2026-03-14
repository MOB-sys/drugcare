"""식품 라우터 — 식품 검색 및 상세 조회."""

from fastapi import APIRouter, Depends, Path, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.food import FoodDetail, FoodSearchItem
from src.backend.services import food_service
from src.backend.utils.response import error_response, success_response

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get(
    "/search",
    response_model=ApiResponse[PaginatedData[FoodSearchItem]],
    summary="식품 검색",
    description="식품명 등으로 식품을 검색합니다.",
)
async def search_foods(
    q: str = Query("", max_length=200, description="검색어 (식품명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 검색 엔드포인트.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[PaginatedData[FoodSearchItem]] 포맷의 dict.
    """
    result = await food_service.search_foods(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/suggest",
    response_model=ApiResponse[list[dict]],
    summary="식품 검색 자동완성",
    description="검색어에 대한 식품 이름 자동완성 제안을 반환합니다.",
)
async def suggest_foods(
    q: str = Query("", min_length=2, max_length=100, description="검색어 (2자 이상)"),
    limit: int = Query(10, ge=1, le=20, description="최대 결과 수"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 자동완성 제안 엔드포인트."""
    result = await food_service.suggest_foods(db, redis, q, limit)
    return success_response(result)


@router.get(
    "/slugs",
    response_model=ApiResponse[list[str]],
    summary="식품 slug 전체 목록",
    description="SSG generateStaticParams용 전체 slug 목록을 반환합니다.",
)
async def get_food_slugs(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 slug 전체 목록 엔드포인트."""
    slugs = await food_service.get_all_food_slugs(db, redis)
    return success_response(slugs)


@router.get(
    "/count",
    response_model=ApiResponse[int],
    summary="식품 총 건수",
    description="전체 식품 건수를 반환합니다.",
)
async def get_food_count(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 총 건수 엔드포인트."""
    count = await food_service.count_foods(db, redis)
    return success_response(count)


@router.get(
    "/by-slug/{slug}",
    response_model=ApiResponse[FoodDetail],
    summary="식품 slug 조회",
    description="slug로 식품 상세 정보를 조회합니다.",
)
async def get_food_by_slug(
    slug: str = Path(..., max_length=200, pattern=r"^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 slug 조회 엔드포인트."""
    result = await food_service.get_food_by_slug(db, redis, slug)
    if result is None:
        return error_response("식품을 찾을 수 없습니다.", 404)
    return success_response(result)


@router.get(
    "/{food_id}",
    response_model=ApiResponse[FoodDetail],
    summary="식품 상세 조회",
    description="식품 ID로 상세 정보를 조회합니다.",
)
async def get_food_detail(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """식품 상세 조회 엔드포인트.

    Args:
        food_id: 조회할 식품의 내부 ID.
        db: DB 세션 (DI).
        redis: Redis 클라이언트 (DI).

    Returns:
        ApiResponse[FoodDetail] 포맷의 dict 또는 404 에러.
    """
    result = await food_service.get_food_detail(db, redis, food_id)
    if result is None:
        return error_response("식품을 찾을 수 없습니다.", 404)
    return success_response(result)
