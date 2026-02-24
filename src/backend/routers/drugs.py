"""의약품 라우터 — 약물 검색 및 상세 조회 (스텁)."""

from fastapi import APIRouter, Query

from src.backend.schemas.common import ApiResponse, PaginatedData
from src.backend.schemas.drug import DrugDetail, DrugSearchItem
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
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
) -> dict:
    """의약품 검색 엔드포인트 (스텁).

    Phase 2에서 실제 DB 검색으로 구현 예정.

    Args:
        q: 검색어.
        page: 페이지 번호 (1부터 시작).
        page_size: 한 페이지당 결과 수.

    Returns:
        ApiResponse[PaginatedData[DrugSearchItem]] 포맷의 dict.
    """
    paginated = PaginatedData[DrugSearchItem](
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )
    return success_response(paginated.model_dump())


@router.get(
    "/{drug_id}",
    response_model=ApiResponse[DrugDetail],
    summary="의약품 상세 조회",
    description="의약품 ID로 상세 정보를 조회합니다.",
)
async def get_drug_detail(
    drug_id: int,
) -> dict:
    """의약품 상세 조회 엔드포인트 (스텁).

    Phase 2에서 실제 DB 조회로 구현 예정.

    Args:
        drug_id: 조회할 의약품의 내부 ID.

    Returns:
        404 에러 응답 (구현 예정).
    """
    return error_response(
        message=f"의약품 상세 조회 구현 예정입니다. (drug_id={drug_id})",
        status_code=404,
    )
