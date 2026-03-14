"""의약품 라우터 — 약물 검색 및 상세 조회."""

from fastapi import APIRouter, Depends, Path, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.core.redis import get_redis
from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.drug import (
    DrugConditionItem,
    DrugDetail,
    DrugIdentifyItem,
    DrugSearchItem,
    DrugSideEffectItem,
)
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
    q: str = Query("", max_length=200, description="검색어 (제품명, 성분명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
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
    "/suggest",
    response_model=ApiResponse[list[dict]],
    summary="의약품 검색 자동완성",
    description="검색어에 대한 의약품 이름 자동완성 제안을 반환합니다.",
)
async def suggest_drugs(
    q: str = Query("", min_length=2, max_length=100, description="검색어 (2자 이상)"),
    limit: int = Query(10, ge=1, le=20, description="최대 결과 수"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """의약품 자동완성 제안 엔드포인트."""
    result = await drug_service.suggest_drugs(db, redis, q, limit)
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
    "/browse/counts",
    response_model=ApiResponse[dict[str, int]],
    summary="초성/알파벳별 의약품 건수",
    description="초성(ㄱ~ㅎ) 및 알파벳(A~Z)별 의약품 건수를 반환합니다.",
)
async def get_drug_browse_counts(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """초성/알파벳별 의약품 건수 엔드포인트."""
    counts = await drug_service.get_drug_counts_by_letter(db, redis)
    return success_response(counts)


@router.get(
    "/browse",
    response_model=ApiResponse[PaginatedData[DrugSearchItem]],
    summary="초성/알파벳별 의약품 조회",
    description="초성(ㄱ~ㅎ) 또는 알파벳(A~Z)으로 의약품을 조회합니다.",
)
async def browse_drugs(
    letter: str = Query(..., max_length=10, description="초성(ㄱ~ㅎ) 또는 알파벳(A~Z)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(50, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """초성/알파벳별 의약품 조회 엔드포인트."""
    result = await drug_service.browse_drugs_by_letter(db, redis, letter, page, page_size)
    return success_response(result)


@router.get(
    "/side-effects/search",
    response_model=ApiResponse[PaginatedData[DrugSideEffectItem]],
    summary="부작용으로 약물 검색",
    description="부작용 키워드로 해당 부작용이 보고된 의약품을 검색합니다.",
)
async def search_by_side_effect(
    q: str = Query(..., max_length=200, description="부작용 키워드"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """부작용 역검색 엔드포인트."""
    result = await drug_service.search_by_side_effect(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/identify",
    response_model=ApiResponse[PaginatedData[DrugIdentifyItem]],
    summary="약 식별 (모양/색상/각인)",
    description="약의 색상, 모양, 각인 정보로 의약품을 식별합니다.",
)
async def identify_drug(
    color: str = Query(None, max_length=50, description="약 색상"),
    shape: str = Query(None, max_length=50, description="약 모양"),
    imprint: str = Query(None, max_length=50, description="각인 문자"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """약 식별 엔드포인트."""
    result = await drug_service.identify_drug(db, redis, color, shape, imprint, page, page_size)
    return success_response(result)


@router.get(
    "/conditions/search",
    response_model=ApiResponse[PaginatedData[DrugConditionItem]],
    summary="질환별 약물 주의사항 검색",
    description="질환 키워드로 관련 주의사항이 있는 의약품을 검색합니다.",
)
async def search_by_condition(
    q: str = Query(..., max_length=200, description="질환 키워드"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """질환별 약물 주의사항 검색 엔드포인트."""
    result = await drug_service.search_by_condition(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/symptoms/search",
    response_model=ApiResponse[PaginatedData[DrugSearchItem]],
    summary="증상별 약물 검색",
    description="증상 키워드로 효능효과에 해당하는 의약품을 검색합니다.",
)
async def search_by_symptom(
    q: str = Query(..., max_length=200, description="증상 키워드 (예: 두통, 소화불량)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """증상별 약물 검색 엔드포인트."""
    result = await drug_service.search_by_symptom(db, redis, q, page, page_size)
    return success_response(result)


@router.get(
    "/recent",
    response_model=ApiResponse[list[DrugSearchItem]],
    summary="최근 등록 의약품",
    description="최근 N일 이내에 등록된 의약품 목록을 반환합니다.",
)
async def get_recent_drugs(
    days: int = Query(30, ge=1, le=365, description="조회 범위 (일)"),
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> dict:
    """최근 등록 의약품 엔드포인트."""
    result = await drug_service.get_recent_drugs(db, redis, days, limit)
    return success_response(result)


@router.get(
    "/by-slug/{slug}",
    response_model=ApiResponse[DrugDetail],
    summary="의약품 slug 조회",
    description="slug로 의약품 상세 정보를 조회합니다.",
)
async def get_drug_by_slug(
    slug: str = Path(..., max_length=200, pattern=r"^[a-z0-9가-힣ㄱ-ㅎㅏ-ㅣ\-]+$"),
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
