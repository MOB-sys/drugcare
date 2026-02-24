"""의약품(Drug) 서비스 — 검색 및 상세 조회 비즈니스 로직."""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.backend.models.drug import Drug
from src.backend.schemas.drug import DrugDetail, DrugSearchItem
from src.backend.utils.cache import cache_get, cache_set, hash_query, make_cache_key
from src.backend.core.redis import CACHE_TTL_DRUG_DETAIL, CACHE_TTL_DRUG_SEARCH


async def search_drugs(
    db: AsyncSession,
    redis: Redis,
    q: str,
    page: int,
    page_size: int,
) -> dict:
    """의약품을 이름으로 검색한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 ILIKE 검색을 수행한다.
    결과는 PaginatedData[DrugSearchItem] 호환 dict로 반환된다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        q: 검색어 (의약품명).
        page: 페이지 번호 (1-based).
        page_size: 페이지당 결과 수.

    Returns:
        PaginatedData 구조의 dict (items, total, page, page_size, total_pages).
    """
    if not q.strip():
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    cache_key = make_cache_key("drug", "search", hash_query(q), str(page), str(page_size))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    # 검색 조건
    condition = Drug.item_name.ilike(f"%{q}%")

    # 전체 건수 조회
    count_stmt = select(func.count()).select_from(Drug).where(condition)
    total_result = await db.execute(count_stmt)
    total: int = total_result.scalar_one()

    # 페이지네이션 조회
    offset = (page - 1) * page_size
    search_stmt = select(Drug).where(condition).offset(offset).limit(page_size)
    rows = await db.execute(search_stmt)
    drugs = rows.scalars().all()

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    items = [DrugSearchItem.model_validate(drug).model_dump() for drug in drugs]

    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_SEARCH)
    return result


async def get_drug_detail(
    db: AsyncSession,
    redis: Redis,
    drug_id: int,
) -> dict | None:
    """의약품 상세 정보를 조회한다.

    Redis 캐시를 우선 확인하고, 캐시 미스 시 DB에서 PK 조회를 수행한다.

    Args:
        db: 비동기 DB 세션.
        redis: Redis 클라이언트.
        drug_id: 조회할 의약품 ID.

    Returns:
        DrugDetail 구조의 dict 또는 None (존재하지 않는 경우).
    """
    cache_key = make_cache_key("drug", "detail", str(drug_id))
    cached = await cache_get(redis, cache_key)
    if cached is not None:
        return cached

    stmt = select(Drug).where(Drug.id == drug_id)
    row = await db.execute(stmt)
    drug = row.scalar_one_or_none()

    if drug is None:
        return None

    result = DrugDetail.model_validate(drug).model_dump()
    await cache_set(redis, cache_key, result, CACHE_TTL_DRUG_DETAIL)
    return result
