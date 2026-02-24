"""영양제 라우터 — 건강기능식품 검색 (스텁)."""

from fastapi import APIRouter, Query

from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.utils.response import success_response

router = APIRouter(prefix="/supplements", tags=["supplements"])


class SupplementSearchItem(ApiResponse):
    """영양제 검색 결과 아이템 — 임시 인라인 정의.

    Phase 2에서 schemas/supplement.py로 분리 예정.
    """

    pass


@router.get(
    "/search",
    response_model=ApiResponse[PaginatedData[dict]],
    summary="영양제 검색",
    description="제품명, 성분명 등으로 건강기능식품을 검색합니다.",
)
async def search_supplements(
    q: str = Query("", description="검색어 (제품명, 성분명 등)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
) -> dict:
    """건강기능식품 검색 엔드포인트 (스텁).

    Phase 2에서 실제 DB 검색으로 구현 예정.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.

    Returns:
        ApiResponse[PaginatedData] 포맷의 dict.
    """
    paginated = PaginatedData[dict](
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )
    return success_response(paginated.model_dump())
