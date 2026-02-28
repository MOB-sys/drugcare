"""의약품 허가정보 API 수집기 — 성분 상세 정보로 drugs 테이블 보강."""

import asyncio
import json
import logging
import re
from typing import Any

import httpx
from sqlalchemy import cast, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings
from src.backend.models.drug import Drug
from src.data.parsers.edrug_parser import strip_html_tags

logger = logging.getLogger(__name__)

# 의약품 허가정보 상세 API 엔드포인트
PERMISSION_API_URL = (
    "http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService05"
    "/getDrugPrdtPrmsnDtlInq05"
)

# 수집 설정
DEFAULT_NUM_OF_ROWS = 100
REQUEST_DELAY_SEC = 0.2
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 2
REQUEST_TIMEOUT_SEC = 30

# 성분 파싱용 정규식: "성분명 분량단위" 패턴
_INGREDIENT_PATTERN = re.compile(
    r"([가-힣a-zA-Z0-9\s\(\)\-\[\]]+?)\s+"
    r"(\d+(?:\.\d+)?)\s*"
    r"(mg|g|μg|mcg|mL|IU|%|KU|밀리그램|그램|마이크로그램)?",
)


def parse_permission_ingredients(material_name: str | None) -> list[dict[str, str | None]]:
    """허가정보 API의 material_name 필드를 구조화된 성분 리스트로 파싱한다.

    허가정보 API의 성분 형식은 e약은요보다 상세하며,
    "총량 : ... | 성분명1|분량1|단위1|규격1|..." 형태를 취할 수 있다.

    Args:
        material_name: 허가정보 API의 원료성분 텍스트.

    Returns:
        구조화된 성분 리스트. [{"name": str, "amount": str|None, "unit": str|None}]
    """
    if not material_name:
        return []

    # HTML 태그 제거
    cleaned = strip_html_tags(material_name)
    if not cleaned:
        return []

    ingredients: list[dict[str, str | None]] = []

    # 파이프(|) 구분 형식
    if "|" in cleaned:
        separator = ";" if ";" in cleaned else ","
        parts = cleaned.split(separator)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # "총량" 헤더 건너뛰기
            if part.startswith("총량"):
                continue

            fields = [f.strip() for f in part.split("|")]
            if len(fields) >= 1 and fields[0]:
                ingredient: dict[str, str | None] = {"name": fields[0]}
                ingredient["amount"] = fields[1] if len(fields) > 1 and fields[1] else None
                ingredient["unit"] = fields[2] if len(fields) > 2 and fields[2] else None
                ingredients.append(ingredient)
    else:
        # 패턴 매칭으로 성분 추출 시도
        matches = _INGREDIENT_PATTERN.findall(cleaned)
        if matches:
            for name, amount, unit in matches:
                name = name.strip()
                if name:
                    ingredients.append({
                        "name": name,
                        "amount": amount if amount else None,
                        "unit": unit if unit else None,
                    })
        elif cleaned:
            # 패턴 매칭 실패 시 전체를 하나의 성분으로
            ingredients.append({"name": cleaned, "amount": None, "unit": None})

    return ingredients


class DrugPermissionCollector:
    """의약품 허가정보 API 수집기.

    이미 drugs 테이블에 존재하는 의약품의 item_seq를 기반으로
    허가정보 API에서 상세 성분 정보를 조회하여 ingredients JSONB를 보강한다.

    Attributes:
        service_key: 공공데이터포털 API 인증키.
        client: httpx 비동기 HTTP 클라이언트.
        stats: 수집 통계 (total, updated, skipped, errors).
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        """수집기를 초기화한다.

        Args:
            client: 외부에서 주입할 httpx.AsyncClient. None이면 내부 생성.
        """
        settings = get_settings()
        self.service_key = settings.DATA_GO_KR_SERVICE_KEY
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC)
        self.stats: dict[str, int] = {
            "total": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

    async def _request_page(
        self,
        page_no: int,
        item_seq: str | None = None,
    ) -> dict[str, Any] | None:
        """허가정보 API 단일 페이지를 조회한다.

        Args:
            page_no: 페이지 번호.
            item_seq: 특정 품목기준코드로 필터링. None이면 전체 조회.

        Returns:
            API 응답 JSON. 실패 시 None.
        """
        params: dict[str, str] = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(DEFAULT_NUM_OF_ROWS),
            "type": "json",
        }

        if item_seq:
            params["item_seq"] = item_seq

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.get(PERMISSION_API_URL, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "허가정보 API HTTP 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "허가정보 API 요청 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except Exception as e:
                logger.warning(
                    "허가정보 API 예상치 못한 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY_SEC * attempt
                await asyncio.sleep(delay)

        logger.error("허가정보 API 최대 재시도 횟수 초과 (page=%d)", page_no)
        return None

    def _extract_items(self, response_data: dict[str, Any]) -> list[dict[str, Any]]:
        """API 응답에서 아이템 리스트를 추출한다.

        Args:
            response_data: API 응답 JSON.

        Returns:
            아이템 딕셔너리 리스트.
        """
        try:
            body = response_data.get("body", {})
            items = body.get("items", [])

            if not items:
                return []

            if isinstance(items, dict):
                items = [items]

            return items

        except (AttributeError, TypeError) as e:
            logger.warning("허가정보 API 응답 파싱 실패: %s", e)
            return []

    def _extract_total_count(self, response_data: dict[str, Any]) -> int:
        """API 응답에서 전체 건수를 추출한다.

        Args:
            response_data: API 응답 JSON.

        Returns:
            전체 건수. 파싱 실패 시 0.
        """
        try:
            body = response_data.get("body", {})
            return int(body.get("totalCount", 0))
        except (ValueError, TypeError, AttributeError):
            return 0

    async def _update_drug_ingredients(
        self,
        session: AsyncSession,
        item_seq: str,
        ingredients: list[dict[str, str | None]],
    ) -> bool:
        """특정 약물의 ingredients JSONB 컬럼을 업데이트한다.

        Args:
            session: 비동기 DB 세션.
            item_seq: 업데이트할 약물의 품목기준코드.
            ingredients: 구조화된 성분 리스트.

        Returns:
            업데이트 성공 시 True.
        """
        if not ingredients:
            return False

        update_sql = text("""
            UPDATE drugs
            SET ingredients = CAST(:ingredients AS jsonb),
                updated_at = NOW()
            WHERE item_seq = :item_seq
        """)

        result = await session.execute(
            update_sql,
            {
                "item_seq": item_seq,
                "ingredients": json.dumps(ingredients, ensure_ascii=False),
            },
        )

        return result.rowcount > 0  # type: ignore[union-attr]

    async def collect(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> dict[str, int]:
        """허가정보 API에서 성분 상세 정보를 수집하여 drugs 테이블을 보강한다.

        이미 DB에 존재하는 약물만 대상으로 하며,
        ingredients 필드가 비어있거나 불완전한 약물을 우선 업데이트한다.

        Args:
            session: 비동기 DB 세션.
            max_pages: 최대 수집 페이지 수. None이면 전량 수집.

        Returns:
            수집 통계 딕셔너리.
        """
        logger.info("허가정보 수집 시작 — drugs.ingredients 보강")

        # DB에서 성분 정보가 없거나 빈 약물 목록 조회
        result = await session.execute(
            select(Drug.item_seq).where(
                (Drug.ingredients.is_(None))
                | (Drug.ingredients == cast("[]", JSONB))
                | (Drug.ingredients == cast("null", JSONB))
            )
        )
        target_seqs = [row[0] for row in result.fetchall()]

        if not target_seqs:
            logger.info("보강 대상 약물 없음 — 전량 페이지네이션 수집 시작")
            await self._collect_all_pages(session, max_pages)
        else:
            logger.info("보강 대상 약물: %d건", len(target_seqs))
            await self._collect_by_item_seqs(session, target_seqs)

        await session.commit()

        logger.info(
            "허가정보 수집 완료 — 대상: %d, 갱신: %d, 건너뜀: %d, 오류: %d",
            self.stats["total"],
            self.stats["updated"],
            self.stats["skipped"],
            self.stats["errors"],
        )

        return self.stats

    async def _collect_by_item_seqs(
        self,
        session: AsyncSession,
        item_seqs: list[str],
    ) -> None:
        """특정 품목기준코드 목록에 대해 허가정보를 개별 조회한다.

        Args:
            session: 비동기 DB 세션.
            item_seqs: 조회할 품목기준코드 리스트.
        """
        for idx, item_seq in enumerate(item_seqs):
            self.stats["total"] += 1

            await asyncio.sleep(REQUEST_DELAY_SEC)

            response_data = await self._request_page(1, item_seq=item_seq)
            if response_data is None:
                self.stats["errors"] += 1
                continue

            items = self._extract_items(response_data)
            if not items:
                self.stats["skipped"] += 1
                continue

            await self._process_permission_item(session, items[0])

            if (idx + 1) % 50 == 0:
                logger.info(
                    "허가정보 진행: %d/%d (갱신: %d)",
                    idx + 1, len(item_seqs), self.stats["updated"],
                )

    async def _collect_all_pages(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> None:
        """전체 허가정보를 페이지네이션으로 수집한다.

        Args:
            session: 비동기 DB 세션.
            max_pages: 최대 수집 페이지 수.
        """
        first_response = await self._request_page(1)
        if first_response is None:
            logger.error("허가정보 첫 페이지 요청 실패")
            return

        total_count = self._extract_total_count(first_response)
        total_pages = (total_count + DEFAULT_NUM_OF_ROWS - 1) // DEFAULT_NUM_OF_ROWS

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info("허가정보 전체 %d건, %d페이지", total_count, total_pages)

        # 첫 페이지 처리
        for item in self._extract_items(first_response):
            self.stats["total"] += 1
            await self._process_permission_item(session, item)

        # 나머지 페이지
        for page_no in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY_SEC)

            response_data = await self._request_page(page_no)
            if response_data is None:
                self.stats["errors"] += 1
                continue

            for item in self._extract_items(response_data):
                self.stats["total"] += 1
                await self._process_permission_item(session, item)

            if page_no % 10 == 0:
                logger.info(
                    "허가정보 진행: %d/%d페이지 (갱신: %d)",
                    page_no, total_pages, self.stats["updated"],
                )

    async def _process_permission_item(
        self,
        session: AsyncSession,
        raw_item: dict[str, Any],
    ) -> None:
        """단일 허가정보 아이템의 성분을 파싱하여 DB를 업데이트한다.

        Args:
            session: 비동기 DB 세션.
            raw_item: 허가정보 API 응답 아이템.
        """
        try:
            # item_seq 추출
            item_seq = (
                raw_item.get("ITEM_SEQ")
                or raw_item.get("itemSeq")
                or raw_item.get("item_seq")
            )
            if not item_seq:
                self.stats["skipped"] += 1
                return

            item_seq = str(item_seq).strip()

            # material_name 추출
            material_name = (
                raw_item.get("MATERIAL_NAME")
                or raw_item.get("materialName")
                or raw_item.get("material_name")
            )

            # 성분 파싱
            ingredients = parse_permission_ingredients(material_name)
            if not ingredients:
                self.stats["skipped"] += 1
                return

            # DB 업데이트
            updated = await self._update_drug_ingredients(
                session, item_seq, ingredients,
            )

            if updated:
                self.stats["updated"] += 1
            else:
                self.stats["skipped"] += 1

        except Exception as e:
            logger.error("허가정보 아이템 처리 오류: %s", e)
            self.stats["errors"] += 1

    async def close(self) -> None:
        """내부 생성한 HTTP 클라이언트를 종료한다."""
        if not self._external_client:
            await self.client.aclose()
