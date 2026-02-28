"""DUR 안전성 정보 수집기 — 임부금기·노인주의·용량주의·투여기간주의·효능군중복."""

import asyncio
import logging
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.config import get_settings
from src.data.parsers.edrug_parser import strip_html_tags

logger = logging.getLogger(__name__)

# DUR 안전성 하위 API 목록
DUR_SAFETY_APIS: list[dict[str, str]] = [
    {
        "dur_type": "pregnancy",
        "type_name": "임부금기",
        "url": (
            "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
            "/getPwnmTabooInfoList03"
        ),
    },
    {
        "dur_type": "elderly",
        "type_name": "노인주의",
        "url": (
            "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
            "/getOdsnAtentInfoList03"
        ),
    },
    {
        "dur_type": "dosage",
        "type_name": "용량주의",
        "url": (
            "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
            "/getCpctyAtentInfoList03"
        ),
    },
    {
        "dur_type": "duration",
        "type_name": "투여기간주의",
        "url": (
            "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
            "/getMdctnPdAtentInfoList03"
        ),
    },
    {
        "dur_type": "efficacy_dup",
        "type_name": "효능군중복",
        "url": (
            "http://apis.data.go.kr/1471000/DURPrdlstInfoService03"
            "/getEfcyDplctInfoList03"
        ),
    },
]

DEFAULT_NUM_OF_ROWS = 100
REQUEST_DELAY_SEC = 0.2
MAX_RETRIES = 3
RETRY_BASE_DELAY_SEC = 2
REQUEST_TIMEOUT_SEC = 30


class DURSafetyCollector:
    """DUR 안전성 정보 수집기.

    5개 하위 API(임부금기, 노인주의, 용량주의, 투여기간주의, 효능군중복)에서
    약물별 안전성 경고 데이터를 수집하여 drug_dur_info 테이블에 저장한다.

    Attributes:
        service_key: 공공데이터포털 API 인증키.
        client: httpx 비동기 HTTP 클라이언트.
        stats: 수집 통계.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
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

    async def _request_page(
        self, url: str, page_no: int,
    ) -> dict[str, Any] | None:
        """API 단일 페이지를 조회한다."""
        params = {
            "serviceKey": self.service_key,
            "pageNo": str(page_no),
            "numOfRows": str(DEFAULT_NUM_OF_ROWS),
            "type": "json",
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "DUR Safety API HTTP 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except httpx.RequestError as e:
                logger.warning(
                    "DUR Safety API 요청 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )
            except Exception as e:
                logger.warning(
                    "DUR Safety API 예상치 못한 오류 (page=%d, attempt=%d/%d): %s",
                    page_no, attempt, MAX_RETRIES, e,
                )

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY_SEC * attempt
                await asyncio.sleep(delay)

        return None

    def _extract_items(
        self, response_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        try:
            body = response_data.get("body", {})
            items = body.get("items", [])
            if not items:
                return []
            if isinstance(items, dict):
                items = [items]
            return items
        except (AttributeError, TypeError):
            return []

    def _extract_total_count(self, response_data: dict[str, Any]) -> int:
        try:
            body = response_data.get("body", {})
            return int(body.get("totalCount", 0))
        except (ValueError, TypeError, AttributeError):
            return 0

    def _parse_item(
        self,
        raw_item: dict[str, Any],
        dur_type: str,
        type_name: str,
    ) -> dict[str, Any] | None:
        """API 응답 아이템을 drug_dur_info 삽입용 딕셔너리로 변환한다."""
        item_seq = (
            raw_item.get("ITEM_SEQ")
            or raw_item.get("itemSeq")
            or raw_item.get("item_seq")
        )
        if not item_seq:
            return None

        item_seq = str(item_seq).strip()

        ingr_code = (
            raw_item.get("INGR_CODE")
            or raw_item.get("ingrCode")
            or ""
        )
        ingr_code = str(ingr_code).strip() if ingr_code else ""

        ingr_name = (
            raw_item.get("INGR_NAME")
            or raw_item.get("ingrName")
            or ""
        )

        ingr_eng_name = (
            raw_item.get("INGR_ENG_NAME")
            or raw_item.get("ingrEngName")
            or ""
        )

        prohibition_content = (
            raw_item.get("PROHBT_CONTENT")
            or raw_item.get("prohbtContent")
        )
        if prohibition_content:
            prohibition_content = strip_html_tags(str(prohibition_content))

        remark = raw_item.get("REMARK") or raw_item.get("remark")
        if remark:
            remark = strip_html_tags(str(remark))

        notification_date = (
            raw_item.get("NOTIFICATION_DATE")
            or raw_item.get("notificationDate")
            or ""
        )

        source_id = f"DUR_{dur_type}_{item_seq}_{ingr_code}"

        return {
            "item_seq": item_seq,
            "dur_type": dur_type,
            "type_name": type_name,
            "ingr_code": ingr_code,
            "ingr_name": str(ingr_name).strip() if ingr_name else None,
            "ingr_eng_name": str(ingr_eng_name).strip() if ingr_eng_name else None,
            "prohibition_content": prohibition_content,
            "remark": remark,
            "notification_date": str(notification_date).strip() if notification_date else None,
            "source_id": source_id,
        }

    async def _upsert_item(
        self,
        session: AsyncSession,
        parsed: dict[str, Any],
        existing_source_ids: set[str],
    ) -> str:
        """단일 레코드를 DB에 upsert한다."""
        source_id = parsed["source_id"]

        if source_id in existing_source_ids:
            update_sql = text("""
                UPDATE drug_dur_info
                SET prohibition_content = :prohibition_content,
                    remark = :remark,
                    updated_at = NOW()
                WHERE source_id = :source_id
            """)
            await session.execute(update_sql, {
                "prohibition_content": parsed.get("prohibition_content"),
                "remark": parsed.get("remark"),
                "source_id": source_id,
            })
            return "updated"

        insert_sql = text("""
            INSERT INTO drug_dur_info (
                item_seq, dur_type, type_name,
                ingr_code, ingr_name, ingr_eng_name,
                prohibition_content, remark,
                notification_date, source_id
            ) VALUES (
                :item_seq, :dur_type, :type_name,
                :ingr_code, :ingr_name, :ingr_eng_name,
                :prohibition_content, :remark,
                :notification_date, :source_id
            )
        """)

        await session.execute(insert_sql, parsed)
        existing_source_ids.add(source_id)
        return "inserted"

    async def _collect_api(
        self,
        session: AsyncSession,
        api_config: dict[str, str],
        existing_source_ids: set[str],
        max_pages: int | None = None,
    ) -> None:
        """단일 DUR 안전성 API의 전체 데이터를 수집한다."""
        dur_type = api_config["dur_type"]
        type_name = api_config["type_name"]
        url = api_config["url"]

        logger.info("[%s] 수집 시작", type_name)

        first_response = await self._request_page(url, 1)
        if first_response is None:
            logger.error("[%s] 첫 페이지 요청 실패", type_name)
            self.stats["errors"] += 1
            return

        total_count = self._extract_total_count(first_response)
        total_pages = (total_count + DEFAULT_NUM_OF_ROWS - 1) // DEFAULT_NUM_OF_ROWS

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info("[%s] 전체 %d건, %d페이지", type_name, total_count, total_pages)

        # 첫 페이지 처리
        await self._process_page(
            first_response, session, dur_type, type_name, existing_source_ids,
        )

        # 나머지 페이지
        for page_no in range(2, total_pages + 1):
            await asyncio.sleep(REQUEST_DELAY_SEC)

            response_data = await self._request_page(url, page_no)
            if response_data is None:
                self.stats["errors"] += 1
                continue

            await self._process_page(
                response_data, session, dur_type, type_name, existing_source_ids,
            )

            if page_no % 20 == 0:
                logger.info(
                    "[%s] 진행: %d/%d페이지",
                    type_name, page_no, total_pages,
                )

        logger.info("[%s] 수집 완료", type_name)

    async def _process_page(
        self,
        response_data: dict[str, Any],
        session: AsyncSession,
        dur_type: str,
        type_name: str,
        existing_source_ids: set[str],
    ) -> None:
        """단일 페이지의 모든 아이템을 처리한다."""
        items = self._extract_items(response_data)

        for raw_item in items:
            self.stats["fetched"] += 1

            try:
                parsed = self._parse_item(raw_item, dur_type, type_name)
                if parsed is None:
                    self.stats["skipped"] += 1
                    continue

                action = await self._upsert_item(
                    session, parsed, existing_source_ids,
                )
                self.stats[action] += 1

            except Exception as e:
                logger.error("DUR Safety 아이템 처리 오류: %s", e)
                self.stats["errors"] += 1

    async def collect(
        self,
        session: AsyncSession,
        max_pages: int | None = None,
    ) -> dict[str, int]:
        """5개 DUR 안전성 API에서 전체 데이터를 수집한다."""
        logger.info("DUR 안전성 정보 수집 시작 (5개 API)")

        # 기존 source_id 로드
        result = await session.execute(
            text("SELECT source_id FROM drug_dur_info WHERE source_id IS NOT NULL")
        )
        existing_source_ids = {row[0] for row in result.fetchall()}
        logger.info("기존 DUR 안전성 정보: %d건", len(existing_source_ids))

        for api_config in DUR_SAFETY_APIS:
            await self._collect_api(
                session, api_config, existing_source_ids, max_pages,
            )

        await session.commit()

        logger.info(
            "DUR 안전성 수집 완료 — 수집: %d, 삽입: %d, 갱신: %d, 건너뜀: %d, 오류: %d",
            self.stats["fetched"],
            self.stats["inserted"],
            self.stats["updated"],
            self.stats["skipped"],
            self.stats["errors"],
        )

        return self.stats

    async def close(self) -> None:
        """내부 생성한 HTTP 클라이언트를 종료한다."""
        if not self._external_client:
            await self.client.aclose()
