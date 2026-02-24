"""DUR 병용금기 수집기 단위 테스트 — httpx 응답 모킹."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.data.scrapers.dur_interaction_collector import DURInteractionCollector


def _make_api_response(
    items: list[dict],
    total_count: int = 1,
) -> httpx.Response:
    """테스트용 DUR API 응답을 생성한다.

    Args:
        items: 응답 아이템 리스트.
        total_count: 전체 건수.

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
        status_code=200,
        json=body,
        request=httpx.Request("GET", "http://test"),
    )


def _make_dur_item(
    item_seq: str = "200000001",
    item_name: str = "테스트약A",
    mixture_item_seq: str = "200000002",
    mixture_item_name: str = "테스트약B",
    prohibition_content: str = "병용 시 부작용 위험 증가",
) -> dict:
    """테스트용 DUR 병용금기 아이템을 생성한다.

    Args:
        item_seq: 약물 A 품목기준코드.
        item_name: 약물 A 제품명.
        mixture_item_seq: 약물 B 품목기준코드.
        mixture_item_name: 약물 B 제품명.
        prohibition_content: 금기 내용.

    Returns:
        DUR API 응답 형식의 딕셔너리.
    """
    return {
        "ITEM_SEQ": item_seq,
        "ITEM_NAME": item_name,
        "ENTP_NAME": "제약사A",
        "MAIN_INGR": "성분A",
        "MIXTURE_ITEM_SEQ": mixture_item_seq,
        "MIXTURE_ITEM_NAME": mixture_item_name,
        "MIXTURE_ENTP_NAME": "제약사B",
        "MIXTURE_MAIN_INGR": "성분B",
        "PROHBT_CONTENT": prohibition_content,
        "REMARK": None,
        "TYPE_NAME": "병용금기",
    }


class TestDURCollectorRequestPage:
    """_request_page 메서드 테스트."""

    @pytest.mark.asyncio
    async def test_successful_request(self) -> None:
        """정상 응답을 반환한다."""
        response = _make_api_response([_make_dur_item()])
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=response)

        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = DURInteractionCollector(client=mock_client)

        result = await collector._request_page(1)

        assert result is not None
        assert "body" in result

    @pytest.mark.asyncio
    async def test_returns_none_after_max_retries(self) -> None:
        """최대 재시도 후 None을 반환한다."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(
            side_effect=httpx.RequestError("timeout")
        )

        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = DURInteractionCollector(client=mock_client)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await collector._request_page(1)

        assert result is None
        assert mock_client.get.call_count == 3


class TestDURCollectorExtract:
    """_extract_items, _extract_total_count 테스트."""

    def _make_collector(self) -> DURInteractionCollector:
        """테스트용 수집기 인스턴스를 생성한다.

        Returns:
            모킹된 설정의 수집기.
        """
        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            return DURInteractionCollector(client=AsyncMock())

    def test_extract_items_normal(self) -> None:
        """정상 응답에서 아이템을 추출한다."""
        collector = self._make_collector()
        items = [_make_dur_item(), _make_dur_item(item_seq="200000003")]
        response = {"body": {"items": items, "totalCount": 2}}

        result = collector._extract_items(response)
        assert len(result) == 2

    def test_extract_items_empty(self) -> None:
        """빈 응답에서 빈 리스트를 반환한다."""
        collector = self._make_collector()
        response: dict = {"body": {"items": [], "totalCount": 0}}

        result = collector._extract_items(response)
        assert result == []

    def test_extract_total_count(self) -> None:
        """전체 건수를 추출한다."""
        collector = self._make_collector()
        response = {"body": {"totalCount": 12345}}
        assert collector._extract_total_count(response) == 12345


class TestDURCollectorBuildLookup:
    """_build_drug_lookup 테스트."""

    @pytest.mark.asyncio
    async def test_build_lookup(self) -> None:
        """DB에서 약물 lookup을 올바르게 생성한다."""
        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = DURInteractionCollector(client=AsyncMock())

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (1, "200000001", "테스트약A"),
            (2, "200000002", "테스트약B"),
        ]
        mock_session.execute = AsyncMock(return_value=mock_result)

        lookup = await collector._build_drug_lookup(mock_session)

        assert len(lookup) == 2
        assert lookup["200000001"]["id"] == 1
        assert lookup["200000001"]["name"] == "테스트약A"
        assert lookup["200000002"]["id"] == 2


class TestDURCollectorCollect:
    """collect 메서드 통합 테스트."""

    @pytest.mark.asyncio
    async def test_collect_skips_when_no_drugs(self) -> None:
        """DB에 약물이 없으면 수집을 건너뛴다."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)

        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = DURInteractionCollector(client=mock_client)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []  # 약물 없음
        mock_session.execute = AsyncMock(return_value=mock_result)

        stats = await collector.collect(mock_session)

        assert stats["fetched"] == 0
        assert stats["inserted"] == 0
        # API 호출 없어야 함
        mock_client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_collect_single_page(self) -> None:
        """단일 페이지 수집이 올바르게 동작한다."""
        dur_item = _make_dur_item()
        api_response = _make_api_response([dur_item], total_count=1)

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=api_response)

        with patch("src.data.scrapers.dur_interaction_collector.get_settings") as mock_settings:
            mock_settings.return_value.DATA_GO_KR_SERVICE_KEY = "test_key"
            collector = DURInteractionCollector(client=mock_client)

        # DB 모킹: 약물 lookup + 기존 source_id + upsert
        call_count = 0
        drug_result = MagicMock()
        drug_result.fetchall.return_value = [
            (1, "200000001", "테스트약A"),
            (2, "200000002", "테스트약B"),
        ]

        source_id_result = MagicMock()
        source_id_result.fetchall.return_value = []  # 기존 DUR 없음

        upsert_result = MagicMock()
        upsert_result.rowcount = 1

        async def mock_execute(*args, **kwargs):
            """순서대로 다른 결과를 반환하는 모킹 함수."""
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return drug_result
            elif call_count == 2:
                return source_id_result
            return upsert_result

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=mock_execute)
        mock_session.commit = AsyncMock()

        stats = await collector.collect(mock_session, max_pages=1)

        assert stats["fetched"] == 1
        mock_session.commit.assert_called_once()
