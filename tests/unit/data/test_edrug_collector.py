"""e약은요 수집기 단위 테스트 — httpx 응답 모킹."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.data.scrapers.edrug_collector import EDrugCollector


def _make_api_response(
    items: list[dict],
    total_count: int = 1,
    status_code: int = 200,
) -> httpx.Response:
    """테스트용 API 응답 객체를 생성한다.

    Args:
        items: 응답에 포함할 아이템 리스트.
        total_count: 전체 건수.
        status_code: HTTP 상태 코드.

    Returns:
        모킹된 httpx.Response.
    """
    body = {
        "body": {
            "items": items,
            "totalCount": total_count,
            "pageNo": 1,
            "numOfRows": 100,
        }
    }
    return httpx.Response(
        status_code=status_code,
        json=body,
        request=httpx.Request("GET", "http://test"),
    )


def _make_drug_item(
    item_seq: str = "200000001",
    item_name: str = "테스트약",
    entp_name: str = "테스트제약",
    efcy_qesitm: str = "<p>두통에 효과</p>",
    material_name: str = "아세트아미노펜|500|mg",
) -> dict:
    """테스트용 약물 아이템을 생성한다.

    Args:
        item_seq: 품목기준코드.
        item_name: 제품명.
        entp_name: 업체명.
        efcy_qesitm: 효능효과 (HTML 포함).
        material_name: 원료성분.

    Returns:
        API 응답 형식의 약물 딕셔너리.
    """
    return {
        "itemSeq": item_seq,
        "itemName": item_name,
        "entpName": entp_name,
        "etcOtcCode": "일반의약품",
        "classNo": "01140",
        "chart": "흰색 원형 정제",
        "barCode": "8806490012345",
        "materialName": material_name,
        "efcyQesitm": efcy_qesitm,
        "useMethodQesitm": "<p>1회 1정</p>",
        "atpnWarnQesitm": None,
        "atpnQesitm": "<p>간장애 주의</p>",
        "intrcQesitm": "<p>와파린과 상호작용</p>",
        "seQesitm": "<p>구역, 발진</p>",
        "depositMethodQesitm": "실온보관",
        "itemImage": "https://example.com/drug.jpg",
    }


class TestEDrugCollectorRequestPage:
    """_request_page 메서드 테스트."""

    @pytest.mark.asyncio
    async def test_successful_request(self) -> None:
        """정상 응답을 올바르게 반환한다."""
        mock_response = _make_api_response([_make_drug_item()])
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=mock_client)

        result = await collector._request_page(1)

        assert result is not None
        assert "body" in result
        mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_http_error(self) -> None:
        """HTTP 오류 시 재시도한다."""
        error_response = httpx.Response(
            status_code=500,
            request=httpx.Request("GET", "http://test"),
        )
        success_response = _make_api_response([_make_drug_item()])

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=[
                httpx.HTTPStatusError(
                    "500 error",
                    request=httpx.Request("GET", "http://test"),
                    response=error_response,
                ),
                success_response,
            ]
        )

        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=mock_client)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await collector._request_page(1)

        assert result is not None
        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_none_after_max_retries(self) -> None:
        """최대 재시도 후 None을 반환한다."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=httpx.RequestError("connection failed")
        )

        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=mock_client)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await collector._request_page(1)

        assert result is None
        assert mock_client.get.call_count == 3  # MAX_RETRIES


class TestEDrugCollectorExtract:
    """_extract_items, _extract_total_count 테스트."""

    def test_extract_items_normal(self) -> None:
        """정상 응답에서 아이템을 추출한다."""
        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=AsyncMock())

        items = [_make_drug_item(), _make_drug_item(item_seq="200000002")]
        response = {"body": {"items": items, "totalCount": 2}}

        result = collector._extract_items(response)
        assert len(result) == 2

    def test_extract_items_empty(self) -> None:
        """빈 응답에서 빈 리스트를 반환한다."""
        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=AsyncMock())

        response: dict = {"body": {"items": [], "totalCount": 0}}
        result = collector._extract_items(response)
        assert result == []

    def test_extract_items_single_dict(self) -> None:
        """단일 아이템(dict)을 리스트로 감싼다."""
        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=AsyncMock())

        item = _make_drug_item()
        response = {"body": {"items": item, "totalCount": 1}}

        result = collector._extract_items(response)
        assert len(result) == 1
        assert result[0]["itemSeq"] == "200000001"

    def test_extract_total_count(self) -> None:
        """전체 건수를 올바르게 추출한다."""
        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=AsyncMock())

        response = {"body": {"totalCount": 54321}}
        assert collector._extract_total_count(response) == 54321

    def test_extract_total_count_missing(self) -> None:
        """totalCount가 없으면 0을 반환한다."""
        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=AsyncMock())

        response: dict = {"body": {}}
        assert collector._extract_total_count(response) == 0


class TestEDrugCollectorCollect:
    """collect 메서드 통합 테스트 (DB 모킹)."""

    @pytest.mark.asyncio
    async def test_collect_single_page(self) -> None:
        """단일 페이지 수집이 올바르게 동작한다."""
        item = _make_drug_item()
        response = _make_api_response([item], total_count=1)

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=response)

        with patch("src.data.scrapers.edrug_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = EDrugCollector(client=mock_client)

        # DB 세션 모킹
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []  # 기존 데이터 없음
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        stats = await collector.collect(mock_session, max_pages=1)

        assert stats["fetched"] == 1
        # execute는 기존 데이터 로드 + upsert로 여러 번 호출됨
        assert mock_session.execute.call_count >= 1
        mock_session.commit.assert_called_once()
