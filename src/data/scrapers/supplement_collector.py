"""식약처 건강기능식품 품목제조신고 API(C003) 수집기 — supplements 테이블 적재."""

import asyncio
import json
import logging
import re
import unicodedata
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings

logger = logging.getLogger(__name__)

# 식품안전나라 건강기능식품 API (C003)
SUPPLEMENT_API_URL = (
    "http://openapi.foodsafetykorea.go.kr/api"
)

# 수집 설정
BATCH_SIZE = 100  # 한 번에 가져올 건수
REQUEST_DELAY_SEC = 0.3
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 2
REQUEST_TIMEOUT_SEC = 30


def _slugify(name: str, report_no: str) -> str:
    """제품명 + 신고번호로 URL-safe slug를 생성한다."""
    # 신고번호 기반 slug (고유성 보장)
    cleaned = re.sub(r"[^0-9]", "", report_no)
    return f"supp-{cleaned}" if cleaned else f"supp-{abs(hash(name)) % 10**8}"


def _parse_raw_materials(raw: str | None) -> list[dict[str, str | None]]:
    """원재료명(RAWMTRL_NM) 텍스트를 구조화된 성분 리스트로 파싱한다."""
    if not raw:
        return []

    ingredients: list[dict[str, str | None]] = []
    # 쉼표 또는 세미콜론으로 분리
    parts = re.split(r"[,;]", raw)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 괄호 내용은 부가 정보
        name = re.sub(r"\s*\(.*?\)\s*", "", part).strip()
        if name:
            ingredients.append({"name": name, "amount": None, "unit": None})

    return ingredients


def _extract_category(functionality: str | None, raw_materials: str | None) -> str:
    """기능성 내용이나 원재료명에서 카테고리를 추론한다."""
    text_pool = f"{functionality or ''} {raw_materials or ''}".lower()

    category_keywords = {
        "프로바이오틱스": ["프로바이오틱스", "유산균", "비피더스", "락토바실러스"],
        "비타민": ["비타민", "vitamin"],
        "미네랄": ["칼슘", "마그네슘", "아연", "철분", "셀레늄", "칼슘"],
        "오메가-3": ["오메가", "omega", "epa", "dha", "피쉬오일"],
        "루테인": ["루테인", "지아잔틴", "눈건강"],
        "홍삼": ["홍삼", "인삼", "진세노사이드"],
        "콜라겐": ["콜라겐", "collagen"],
        "밀크씨슬": ["밀크씨슬", "실리마린", "간건강"],
        "코엔자임Q10": ["코엔자임", "coq10"],
        "글루코사민": ["글루코사민", "관절", "msm"],
    }

    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in text_pool:
                return category

    return "기타"


class SupplementCollector:
    """식약처 건강기능식품 품목제조신고 API(C003) 수집기.

    Attributes:
        service_key: 식품안전나라 API 인증키.
        client: httpx 비동기 HTTP 클라이언트.
        stats: 수집 통계.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self.service_key = settings.FOOD_SAFETY_API_KEY or settings.DATA_GO_KR_SERVICE_KEY
        self._external_client = client is not None
        self.client = client or httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC)
        self.stats: dict[str, int] = {
            "fetched": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

    async def _request_batch(
        self, start_idx: int, end_idx: int,
    ) -> dict[str, Any] | None:
        """API에서 start_idx ~ end_idx 범위의 데이터를 조회한다."""
        url = (
            f"{SUPPLEMENT_API_URL}/{self.service_key}"
            f"/C003/json/{start_idx}/{end_idx}"
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "건강기능식품 API HTTP 오류 (%d~%d, attempt=%d/%d): %s",
                    start_idx, end_idx, attempt, MAX_RETRIES, e,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "건강기능식품 API 요청 오류 (%d~%d, attempt=%d/%d): %s",
                    start_idx, end_idx, attempt, MAX_RETRIES, e,
                )
            except Exception as e:
                logger.warning(
                    "건강기능식품 API 예상치 못한 오류 (%d~%d, attempt=%d/%d): %s",
                    start_idx, end_idx, attempt, MAX_RETRIES, e,
                )

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY_SEC * attempt
                await asyncio.sleep(delay)

        logger.error("건강기능식품 API 최대 재시도 초과 (%d~%d)", start_idx, end_idx)
        return None

    def _extract_items(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """API 응답에서 아이템 리스트를 추출한다."""
        try:
            c003 = data.get("C003", {})
            # 에러 체크
            result_code = c003.get("RESULT", {}).get("CODE", "")
            if result_code != "INFO-000":
                msg = c003.get("RESULT", {}).get("MSG", "")
                logger.warning("API 응답 에러: %s — %s", result_code, msg)
                return []

            rows = c003.get("row", [])
            if isinstance(rows, dict):
                rows = [rows]
            return rows
        except (AttributeError, TypeError) as e:
            logger.warning("응답 파싱 실패: %s", e)
            return []

    def _extract_total_count(self, data: dict[str, Any]) -> int:
        """API 응답에서 전체 건수를 추출한다."""
        try:
            return int(data.get("C003", {}).get("total_count", "0"))
        except (ValueError, TypeError):
            return 0

    async def _upsert_supplement(
        self,
        session: AsyncSession,
        item: dict[str, Any],
        existing_report_nos: set[str],
    ) -> str:
        """단일 건강기능식품 데이터를 DB에 upsert한다."""
        report_no = (item.get("PRDLST_REPORT_NO") or "").strip()
        product_name = (item.get("PRDLST_NM") or "").strip()

        if not product_name:
            return "skipped"

        raw_materials = item.get("RAWMTRL_NM") or ""
        functionality = item.get("PRIMARY_FNCLTY") or ""
        precautions = item.get("IFTKN_ATNT_MATR_CN") or ""
        intake_method = item.get("NTK_MTHD") or ""
        company = (item.get("BSSH_NM") or "").strip()

        ingredients = _parse_raw_materials(raw_materials)
        category = _extract_category(functionality, raw_materials)
        slug = _slugify(product_name, report_no)

        # 주성분: 첫 번째 성분명
        main_ingredient = ingredients[0]["name"] if ingredients else None

        upsert_sql = text("""
            INSERT INTO supplements (
                product_name, slug, company, registration_no,
                main_ingredient, ingredients, functionality,
                precautions, intake_method, category, source
            ) VALUES (
                :product_name, :slug, :company, :registration_no,
                :main_ingredient, CAST(:ingredients AS jsonb), :functionality,
                :precautions, :intake_method, :category, :source
            )
            ON CONFLICT (registration_no) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                slug = EXCLUDED.slug,
                company = EXCLUDED.company,
                main_ingredient = EXCLUDED.main_ingredient,
                ingredients = EXCLUDED.ingredients,
                functionality = EXCLUDED.functionality,
                precautions = EXCLUDED.precautions,
                intake_method = EXCLUDED.intake_method,
                category = EXCLUDED.category,
                source = EXCLUDED.source,
                updated_at = NOW()
        """)

        params = {
            "product_name": product_name,
            "slug": slug,
            "company": company,
            "registration_no": report_no or None,
            "main_ingredient": main_ingredient,
            "ingredients": json.dumps(ingredients, ensure_ascii=False),
            "functionality": functionality or None,
            "precautions": precautions or None,
            "intake_method": intake_method or None,
            "category": category,
            "source": "식약처 C003",
        }

        try:
            await session.execute(upsert_sql, params)
            existing_report_nos.add(report_no)
            return "updated" if report_no in existing_report_nos else "inserted"
        except Exception as e:
            # slug 또는 기타 충돌 시 건너뛰기
            logger.debug("upsert 건너뜀 (%s): %s", product_name, e)
            await session.rollback()
            return "skipped"

    async def collect(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> dict[str, int]:
        """건강기능식품 전체 데이터를 수집하여 supplements 테이블에 저장한다."""
        logger.info("건강기능식품 수집 시작")

        # 기존 registration_no 로드
        result = await session.execute(
            text("SELECT registration_no FROM supplements WHERE registration_no IS NOT NULL")
        )
        existing_report_nos = {row[0] for row in result.fetchall()}
        logger.info("기존 영양제 데이터: %d건", len(existing_report_nos))

        # 첫 배치로 전체 건수 파악
        first_data = await self._request_batch(1, BATCH_SIZE)
        if first_data is None:
            logger.error("첫 배치 요청 실패 — 수집 중단")
            return self.stats

        total_count = self._extract_total_count(first_data)
        total_batches = (total_count + BATCH_SIZE - 1) // BATCH_SIZE

        if max_pages is not None:
            total_batches = min(total_batches, max_pages)

        logger.info("전체 %d건, %d배치 수집 예정 (배치당 %d건)", total_count, total_batches, BATCH_SIZE)

        # 첫 배치 처리
        await self._process_batch(first_data, session, existing_report_nos)

        # 나머지 배치
        for batch_no in range(2, total_batches + 1):
            await asyncio.sleep(REQUEST_DELAY_SEC)

            start = (batch_no - 1) * BATCH_SIZE + 1
            end = batch_no * BATCH_SIZE

            data = await self._request_batch(start, end)
            if data is None:
                self.stats["errors"] += 1
                continue

            await self._process_batch(data, session, existing_report_nos)

            if batch_no % 10 == 0:
                logger.info(
                    "진행: %d/%d배치 (수집: %d, 삽입: %d, 갱신: %d)",
                    batch_no, total_batches,
                    self.stats["fetched"],
                    self.stats["inserted"],
                    self.stats["updated"],
                )

        await session.commit()

        logger.info(
            "건강기능식품 수집 완료 — 수집: %d, 삽입: %d, 갱신: %d, 건너뜀: %d, 오류: %d",
            self.stats["fetched"],
            self.stats["inserted"],
            self.stats["updated"],
            self.stats["skipped"],
            self.stats["errors"],
        )

        return self.stats

    async def _process_batch(
        self,
        data: dict[str, Any],
        session: AsyncSession,
        existing_report_nos: set[str],
    ) -> None:
        """단일 배치의 모든 아이템을 처리한다."""
        items = self._extract_items(data)

        for item in items:
            self.stats["fetched"] += 1
            try:
                action = await self._upsert_supplement(session, item, existing_report_nos)
                self.stats[action] += 1
            except Exception as e:
                logger.error(
                    "아이템 처리 오류 (%s): %s",
                    item.get("PRDLST_NM", "N/A"), e,
                )
                self.stats["errors"] += 1

    async def close(self) -> None:
        """HTTP 클라이언트를 종료한다."""
        if not self._external_client:
            await self.client.aclose()
