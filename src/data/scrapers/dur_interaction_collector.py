"""DUR 병용금기 API 수집기 — 약물 간 상호작용 데이터 수집 및 DB 저장."""

import asyncio
import json
import logging
from typing import Any

import httpx
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings
from src.backend.models.drug import Drug
from src.data.parsers.dur_parser import parse_dur_item
from src.data.validators.interaction_validator import validate_interaction

logger = logging.getLogger(__name__)

# DUR 병용금기 API 엔드포인트
DUR_API_URL = (
    "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
    "/getUsjntTabooInfoList03"
)

# 수집 설정
DEFAULT_NUM_OF_ROWS = 100
REQUEST_DELAY_SEC = 0.2
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 2
REQUEST_TIMEOUT_SEC = 30


class DURInteractionCollector:
    """DUR 병용금기 API 수집기.

    식약처 DUR(Drug Utilization Review) 시스템의 병용금기 정보를
    수집하여 interactions 테이블에 저장한다.
    모든 DUR 병용금기 항목은 severity='danger'로 저장된다.

    Attributes:
        service_key: 공공데이터포털 API 인증키.
        client: httpx 비동기 HTTP 클라이언트.
        stats: 수집 통계 (fetched, inserted, updated, skipped, errors).
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
            "fetched": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

    async def _request_page(self, page_no: int) -> dict[str, Any] | None:
        """DUR API 단일 페이지를 조회한다.

        지수 백오프 재시도를 포함한다 (최대 3회).

        Args:
            page_no: 페이지 번호 (1부터 시작).

        Returns:
            API 응답 JSON. 실패 시 None.
        """
        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(DEFAULT_NUM_OF_ROWS),
            "type": "json",
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.get(DUR_API_URL, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "DUR API HTTP 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "DUR API 요청 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except Exception as e:
                logger.warning(
                    "DUR API 예상치 못한 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY_SEC * attempt
                logger.info("재시도 대기 %.1f초...", delay)
                await asyncio.sleep(delay)

        logger.error("DUR API 최대 재시도 횟수 초과 (page=%d)", page_no)
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
            logger.warning("DUR API 응답 파싱 실패: %s", e)
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

    async def _build_drug_lookup(
        self,
        session: AsyncSession,
    ) -> dict[str, dict[str, Any]]:
        """DB에서 약물 item_seq → {id, name} 매핑 딕셔너리를 생성한다.

        Args:
            session: 비동기 DB 세션.

        Returns:
            item_seq를 키로 하는 약물 정보 딕셔너리.
        """
        result = await session.execute(
            select(Drug.id, Drug.item_seq, Drug.item_name)
        )

        lookup: dict[str, dict[str, Any]] = {}
        for row in result.fetchall():
            lookup[row[1]] = {"id": row[0], "name": row[2]}

        return lookup

    async def _ensure_drug_exists(
        self,
        session: AsyncSession,
        item_seq: str,
        item_name: str,
        drug_lookup: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """약물이 DB에 없으면 기본 레코드를 삽입하고 lookup에 추가한다.

        Args:
            session: 비동기 DB 세션.
            item_seq: 품목기준코드.
            item_name: 제품명.
            drug_lookup: item_seq → {id, name} 매핑.

        Returns:
            약물 정보 딕셔너리 {id, name}. 실패 시 None.
        """
        if item_seq in drug_lookup:
            return drug_lookup[item_seq]

        try:
            slug = f"drug-{item_seq}"
            insert_sql = text("""
                INSERT INTO drugs (item_seq, item_name, slug)
                VALUES (:item_seq, :item_name, :slug)
                ON CONFLICT (item_seq) DO NOTHING
                RETURNING id
            """)
            result = await session.execute(insert_sql, {
                "item_seq": item_seq,
                "item_name": item_name,
                "slug": slug,
            })
            row = result.first()
            if row:
                drug_lookup[item_seq] = {"id": row[0], "name": item_name}
                return drug_lookup[item_seq]
            # ON CONFLICT hit — fetch existing
            fetch_sql = text("SELECT id, item_name FROM drugs WHERE item_seq = :seq")
            result = await session.execute(fetch_sql, {"seq": item_seq})
            row = result.first()
            if row:
                drug_lookup[item_seq] = {"id": row[0], "name": row[1]}
                return drug_lookup[item_seq]
        except Exception as e:
            logger.warning("약물 자동 삽입 실패 (item_seq=%s): %s", item_seq, e)

        return None

    async def _load_existing_source_ids(
        self,
        session: AsyncSession,
    ) -> set[str]:
        """DB에서 이미 존재하는 DUR 상호작용의 source_id 집합을 로드한다.

        Args:
            session: 비동기 DB 세션.

        Returns:
            기존 source_id 집합.
        """
        result = await session.execute(
            text("SELECT source_id FROM interactions WHERE source = 'DUR' AND source_id IS NOT NULL")
        )
        return {row[0] for row in result.fetchall()}

    async def _upsert_interaction(
        self,
        session: AsyncSession,
        parsed: dict[str, Any],
        existing_source_ids: set[str],
    ) -> str:
        """단일 상호작용 데이터를 DB에 upsert한다.

        source_id 기준으로 중복 체크하며, ON CONFLICT는 pair 인덱스를 활용한다.

        Args:
            session: 비동기 DB 세션.
            parsed: 파싱된 상호작용 데이터 딕셔너리.
            existing_source_ids: 기존 source_id 집합.

        Returns:
            수행된 작업: "inserted", "updated", "skipped".
        """
        source_id = parsed.get("source_id")

        # source_id 기반 중복 체크
        is_duplicate = source_id is not None and source_id in existing_source_ids

        if is_duplicate:
            # 기존 레코드 업데이트
            update_sql = text("""
                UPDATE interactions
                SET description = :description,
                    mechanism = :mechanism,
                    recommendation = :recommendation,
                    updated_at = NOW()
                WHERE source_id = :source_id AND source = 'DUR'
            """)

            await session.execute(update_sql, {
                "description": parsed.get("description"),
                "mechanism": parsed.get("mechanism"),
                "recommendation": parsed.get("recommendation"),
                "source_id": source_id,
            })

            return "updated"

        # 새 레코드 삽입
        insert_sql = text("""
            INSERT INTO interactions (
                item_a_type, item_a_id, item_a_name,
                item_b_type, item_b_id, item_b_name,
                severity, description, mechanism, recommendation,
                source, source_id, evidence_level
            ) VALUES (
                :item_a_type, :item_a_id, :item_a_name,
                :item_b_type, :item_b_id, :item_b_name,
                :severity, :description, :mechanism, :recommendation,
                :source, :source_id, :evidence_level
            )
        """)

        await session.execute(insert_sql, {
            "item_a_type": parsed["item_a_type"],
            "item_a_id": parsed["item_a_id"],
            "item_a_name": parsed["item_a_name"],
            "item_b_type": parsed["item_b_type"],
            "item_b_id": parsed["item_b_id"],
            "item_b_name": parsed["item_b_name"],
            "severity": parsed["severity"],
            "description": parsed.get("description"),
            "mechanism": parsed.get("mechanism"),
            "recommendation": parsed.get("recommendation"),
            "source": parsed["source"],
            "source_id": source_id,
            "evidence_level": parsed.get("evidence_level"),
        })

        if source_id:
            existing_source_ids.add(source_id)

        return "inserted"

    async def collect(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> dict[str, int]:
        """DUR 병용금기 API에서 전체 상호작용 데이터를 수집하여 DB에 저장한다.

        수집 순서:
        1. DB에서 약물 lookup 딕셔너리 생성
        2. 기존 DUR 상호작용 source_id 로드
        3. API 페이지네이션 수집 → 파싱 → 검증 → upsert

        Args:
            session: 비동기 DB 세션.
            max_pages: 최대 수집 페이지 수. None이면 전량 수집.

        Returns:
            수집 통계 딕셔너리.
        """
        logger.info("DUR 병용금기 수집 시작")

        # 약물 lookup 생성
        drug_lookup = await self._build_drug_lookup(session)
        logger.info("약물 lookup: %d건", len(drug_lookup))

        if not drug_lookup:
            logger.warning("DB에 약물 데이터 없음 — DUR 수집 건너뜀 (e약은요 먼저 수집)")
            return self.stats

        # 기존 source_id 로드
        existing_source_ids = await self._load_existing_source_ids(session)
        logger.info("기존 DUR 상호작용: %d건", len(existing_source_ids))

        # 첫 페이지
        first_response = await self._request_page(1)
        if first_response is None:
            logger.error("DUR 첫 페이지 요청 실패 — 수집 중단")
            return self.stats

        total_count = self._extract_total_count(first_response)
        total_pages = (total_count + DEFAULT_NUM_OF_ROWS - 1) // DEFAULT_NUM_OF_ROWS

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info(
            "DUR 전체 %d건, %d페이지 수집 예정",
            total_count, total_pages,
        )

        # 첫 페이지 처리
        await self._process_page(
            first_response, session, drug_lookup, existing_source_ids,
        )

        # 나머지 페이지
        for page_no in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY_SEC)

            response_data = await self._request_page(page_no)
            if response_data is None:
                self.stats["errors"] += 1
                continue

            await self._process_page(
                response_data, session, drug_lookup, existing_source_ids,
            )

            if page_no % 10 == 0:
                logger.info(
                    "DUR 진행: %d/%d페이지 (수집: %d, 삽입: %d, 갱신: %d)",
                    page_no, total_pages,
                    self.stats["fetched"],
                    self.stats["inserted"],
                    self.stats["updated"],
                )

        await session.commit()

        logger.info(
            "DUR 수집 완료 — 수집: %d, 삽입: %d, 갱신: %d, 건너뜀: %d, 오류: %d",
            self.stats["fetched"],
            self.stats["inserted"],
            self.stats["updated"],
            self.stats["skipped"],
            self.stats["errors"],
        )

        return self.stats

    async def _process_page(
        self,
        response_data: dict[str, Any],
        session: AsyncSession,
        drug_lookup: dict[str, dict[str, Any]],
        existing_source_ids: set[str],
    ) -> None:
        """단일 페이지의 모든 DUR 아이템을 처리한다.

        Args:
            response_data: API 응답 JSON.
            session: 비동기 DB 세션.
            drug_lookup: item_seq → {id, name} 매핑.
            existing_source_ids: 기존 source_id 집합.
        """
        items = self._extract_items(response_data)

        for raw_item in items:
            self.stats["fetched"] += 1

            try:
                # 파싱 (약물 lookup으로 매칭)
                parsed = parse_dur_item(raw_item, drug_lookup)
                if parsed is None:
                    # 약물이 DB에 없는 경우 자동 삽입 시도
                    from src.data.parsers.dur_parser import _normalize_dur_item
                    normalized = _normalize_dur_item(raw_item)
                    seq_a = str(normalized.get("item_seq", ""))
                    seq_b = str(normalized.get("mixture_item_seq", ""))
                    name_a = normalized.get("item_name", "")
                    name_b = normalized.get("mixture_item_name", "")
                    if seq_a and seq_b and name_a and name_b:
                        await self._ensure_drug_exists(session, seq_a, name_a, drug_lookup)
                        await self._ensure_drug_exists(session, seq_b, name_b, drug_lookup)
                        parsed = parse_dur_item(raw_item, drug_lookup)
                    if parsed is None:
                        self.stats["skipped"] += 1
                        continue

                # 검증
                is_valid, errors = validate_interaction(parsed)
                if not is_valid:
                    logger.warning(
                        "DUR 검증 실패 (source_id=%s): %s",
                        parsed.get("source_id", "N/A"),
                        "; ".join(errors),
                    )
                    self.stats["skipped"] += 1
                    continue

                # DB 저장
                action = await self._upsert_interaction(
                    session, parsed, existing_source_ids,
                )
                self.stats[action] += 1

            except Exception as e:
                logger.error("DUR 아이템 처리 오류: %s", e)
                self.stats["errors"] += 1

    async def close(self) -> None:
        """내부 생성한 HTTP 클라이언트를 종료한다."""
        if not self._external_client:
            await self.client.aclose()
