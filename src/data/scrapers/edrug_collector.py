"""식약처 e약은요 API 수집기 — 의약품 기본정보 수집 및 DB 저장."""

import asyncio
import logging
from typing import Any

import httpx
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings
from src.backend.models.drug import Drug
from src.data.parsers.edrug_parser import parse_drug_item
from src.data.validators.drug_validator import check_duplicate, validate_drug

logger = logging.getLogger(__name__)

# e약은요 API 엔드포인트
EDRUG_API_URL = (
    "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
)

# 수집 설정
DEFAULT_NUM_OF_ROWS = 100
REQUEST_DELAY_SEC = 0.2  # 0.2초 딜레이 (10,000 req/day 제한 준수)
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 2  # 지수 백오프 기본 딜레이 (2s, 4s, 6s)
REQUEST_TIMEOUT_SEC = 30


class EDrugCollector:
    """식약처 e약은요 API 수집기.

    의약품 기본정보(제품명, 성분, 효능, 용법, 주의사항 등)를
    페이지네이션으로 전량 수집하여 drugs 테이블에 upsert한다.

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
        """단일 페이지를 API에서 조회한다.

        지수 백오프 재시도를 포함한다 (최대 3회, 2s/4s/6s).

        Args:
            page_no: 요청할 페이지 번호 (1부터 시작).

        Returns:
            API 응답 JSON 딕셔너리. 실패 시 None.
        """
        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(DEFAULT_NUM_OF_ROWS),
            "type": "json",
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.get(EDRUG_API_URL, params=params)
                response.raise_for_status()

                data = response.json()
                return data

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "e약은요 API HTTP 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "e약은요 API 요청 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except Exception as e:
                logger.warning(
                    "e약은요 API 예상치 못한 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY_SEC * attempt
                logger.info("재시도 대기 %.1f초...", delay)
                await asyncio.sleep(delay)

        logger.error("e약은요 API 최대 재시도 횟수 초과 (page=%d)", page_no)
        return None

    def _extract_items(self, response_data: dict[str, Any]) -> list[dict[str, Any]]:
        """API 응답에서 아이템 리스트를 추출한다.

        Args:
            response_data: API 응답 JSON 전체.

        Returns:
            아이템 딕셔너리 리스트. 데이터가 없으면 빈 리스트.
        """
        try:
            body = response_data.get("body", {})
            items = body.get("items", [])

            # items가 None이거나 빈 경우
            if not items:
                return []

            # 단일 아이템인 경우 리스트로 감싸기
            if isinstance(items, dict):
                items = [items]

            return items

        except (AttributeError, TypeError) as e:
            logger.warning("API 응답 파싱 실패: %s", e)
            return []

    def _extract_total_count(self, response_data: dict[str, Any]) -> int:
        """API 응답에서 전체 아이템 수를 추출한다.

        Args:
            response_data: API 응답 JSON 전체.

        Returns:
            전체 아이템 수. 파싱 실패 시 0.
        """
        try:
            body = response_data.get("body", {})
            return int(body.get("totalCount", 0))
        except (ValueError, TypeError, AttributeError):
            return 0

    async def _load_existing_seqs(self, session: AsyncSession) -> set[str]:
        """DB에 이미 존재하는 품목기준코드 집합을 로드한다.

        Args:
            session: 비동기 DB 세션.

        Returns:
            기존 품목기준코드 집합.
        """
        result = await session.execute(select(Drug.item_seq))
        return {row[0] for row in result.fetchall()}

    async def _upsert_drug(
        self,
        session: AsyncSession,
        parsed: dict[str, Any],
        existing_seqs: set[str],
    ) -> str:
        """단일 의약품 데이터를 DB에 upsert한다.

        PostgreSQL ON CONFLICT DO UPDATE를 raw SQL로 실행한다.

        Args:
            session: 비동기 DB 세션.
            parsed: 파싱된 의약품 데이터 딕셔너리.
            existing_seqs: 기존 품목기준코드 집합 (중복 체크용).

        Returns:
            수행된 작업: "inserted", "updated", "skipped".
        """
        item_seq = parsed.get("item_seq")
        if not item_seq:
            return "skipped"

        is_duplicate = check_duplicate(item_seq, existing_seqs)

        # Upsert SQL (ON CONFLICT DO UPDATE)
        upsert_sql = text("""
            INSERT INTO drugs (
                item_seq, item_name, entp_name, etc_otc_code, class_no,
                chart, bar_code, material_name, ingredients,
                efcy_qesitm, use_method_qesitm, atpn_warn_qesitm,
                atpn_qesitm, intrc_qesitm, se_qesitm,
                deposit_method_qesitm, item_image
            ) VALUES (
                :item_seq, :item_name, :entp_name, :etc_otc_code, :class_no,
                :chart, :bar_code, :material_name, :ingredients::jsonb,
                :efcy_qesitm, :use_method_qesitm, :atpn_warn_qesitm,
                :atpn_qesitm, :intrc_qesitm, :se_qesitm,
                :deposit_method_qesitm, :item_image
            )
            ON CONFLICT (item_seq) DO UPDATE SET
                item_name = EXCLUDED.item_name,
                entp_name = EXCLUDED.entp_name,
                etc_otc_code = EXCLUDED.etc_otc_code,
                class_no = EXCLUDED.class_no,
                chart = EXCLUDED.chart,
                bar_code = EXCLUDED.bar_code,
                material_name = EXCLUDED.material_name,
                ingredients = EXCLUDED.ingredients,
                efcy_qesitm = EXCLUDED.efcy_qesitm,
                use_method_qesitm = EXCLUDED.use_method_qesitm,
                atpn_warn_qesitm = EXCLUDED.atpn_warn_qesitm,
                atpn_qesitm = EXCLUDED.atpn_qesitm,
                intrc_qesitm = EXCLUDED.intrc_qesitm,
                se_qesitm = EXCLUDED.se_qesitm,
                deposit_method_qesitm = EXCLUDED.deposit_method_qesitm,
                item_image = EXCLUDED.item_image,
                updated_at = NOW()
        """)

        import json

        params = {
            "item_seq": parsed.get("item_seq"),
            "item_name": parsed.get("item_name"),
            "entp_name": parsed.get("entp_name"),
            "etc_otc_code": parsed.get("etc_otc_code"),
            "class_no": parsed.get("class_no"),
            "chart": parsed.get("chart"),
            "bar_code": parsed.get("bar_code"),
            "material_name": parsed.get("material_name"),
            "ingredients": json.dumps(
                parsed.get("ingredients", []), ensure_ascii=False
            ),
            "efcy_qesitm": parsed.get("efcy_qesitm"),
            "use_method_qesitm": parsed.get("use_method_qesitm"),
            "atpn_warn_qesitm": parsed.get("atpn_warn_qesitm"),
            "atpn_qesitm": parsed.get("atpn_qesitm"),
            "intrc_qesitm": parsed.get("intrc_qesitm"),
            "se_qesitm": parsed.get("se_qesitm"),
            "deposit_method_qesitm": parsed.get("deposit_method_qesitm"),
            "item_image": parsed.get("item_image"),
        }

        await session.execute(upsert_sql, params)

        # 기존 set에 추가
        existing_seqs.add(item_seq)

        return "updated" if is_duplicate else "inserted"

    async def collect(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> dict[str, int]:
        """e약은요 API에서 전체 의약품 데이터를 수집하여 DB에 저장한다.

        페이지네이션으로 전량 수집하며, 각 요청 간 0.2초 딜레이를 둔다.

        Args:
            session: 비동기 DB 세션.
            max_pages: 최대 수집 페이지 수. None이면 전량 수집.

        Returns:
            수집 통계 딕셔너리 (fetched, inserted, updated, skipped, errors).
        """
        logger.info("e약은요 수집 시작")

        # 기존 데이터 로드
        existing_seqs = await self._load_existing_seqs(session)
        logger.info("기존 약물 데이터: %d건", len(existing_seqs))

        # 첫 페이지 요청으로 전체 건수 파악
        first_response = await self._request_page(1)
        if first_response is None:
            logger.error("첫 페이지 요청 실패 — 수집 중단")
            return self.stats

        total_count = self._extract_total_count(first_response)
        total_pages = (total_count + DEFAULT_NUM_OF_ROWS - 1) // DEFAULT_NUM_OF_ROWS

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info(
            "전체 %d건, %d페이지 수집 예정 (페이지당 %d건)",
            total_count, total_pages, DEFAULT_NUM_OF_ROWS,
        )

        # 첫 페이지 처리
        await self._process_page(first_response, session, existing_seqs)

        # 나머지 페이지 처리
        for page_no in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY_SEC)

            response_data = await self._request_page(page_no)
            if response_data is None:
                self.stats["errors"] += 1
                continue

            await self._process_page(response_data, session, existing_seqs)

            # 중간 진행 로그 (10페이지마다)
            if page_no % 10 == 0:
                logger.info(
                    "진행: %d/%d 페이지 (수집: %d, 삽입: %d, 갱신: %d)",
                    page_no, total_pages,
                    self.stats["fetched"],
                    self.stats["inserted"],
                    self.stats["updated"],
                )

        # 커밋
        await session.commit()

        logger.info(
            "e약은요 수집 완료 — 수집: %d, 삽입: %d, 갱신: %d, 건너뜀: %d, 오류: %d",
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
        existing_seqs: set[str],
    ) -> None:
        """단일 페이지 응답의 모든 아이템을 파싱/검증/저장한다.

        Args:
            response_data: API 응답 JSON.
            session: 비동기 DB 세션.
            existing_seqs: 기존 품목기준코드 집합.
        """
        items = self._extract_items(response_data)

        for raw_item in items:
            self.stats["fetched"] += 1

            try:
                # 파싱
                parsed = parse_drug_item(raw_item)

                # 검증
                is_valid, errors = validate_drug(parsed)
                if not is_valid:
                    logger.warning(
                        "검증 실패 (item_seq=%s): %s",
                        parsed.get("item_seq", "N/A"),
                        "; ".join(errors),
                    )
                    self.stats["skipped"] += 1
                    continue

                # DB 저장
                action = await self._upsert_drug(session, parsed, existing_seqs)
                self.stats[action] += 1

            except Exception as e:
                logger.error(
                    "아이템 처리 오류: %s — %s",
                    raw_item.get("itemSeq", raw_item.get("ITEM_SEQ", "N/A")),
                    e,
                )
                self.stats["errors"] += 1

    async def close(self) -> None:
        """내부 생성한 HTTP 클라이언트를 종료한다."""
        if not self._external_client:
            await self.client.aclose()
