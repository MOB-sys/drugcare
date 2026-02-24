"""파서 단위 테스트 — HTML 태그 제거, 정규화, 파싱."""

import pytest

from src.data.parsers.dur_parser import (
    build_interaction_description,
    parse_dur_item,
)
from src.data.parsers.edrug_parser import (
    normalize_whitespace,
    parse_drug_item,
    parse_material_name,
    strip_html_tags,
)


class TestStripHtmlTags:
    """strip_html_tags 함수 테스트."""

    def test_removes_simple_tags(self) -> None:
        """단순 HTML 태그를 제거한다."""
        assert strip_html_tags("<p>안녕하세요</p>") == "안녕하세요"

    def test_removes_nested_tags(self) -> None:
        """중첩 HTML 태그를 제거한다."""
        html = "<div><p><b>굵은 텍스트</b></p></div>"
        assert strip_html_tags(html) == "굵은 텍스트"

    def test_removes_tags_with_attributes(self) -> None:
        """속성이 있는 태그를 제거한다."""
        html = '<a href="http://example.com">링크</a>'
        assert strip_html_tags(html) == "링크"

    def test_replaces_html_entities(self) -> None:
        """HTML 엔티티를 치환한다."""
        assert strip_html_tags("A &amp; B") == "A & B"
        assert strip_html_tags("A &lt; B") == "A < B"
        assert strip_html_tags("A &gt; B") == "A > B"
        assert strip_html_tags("A&nbsp;B") == "A B"

    def test_normalizes_whitespace(self) -> None:
        """연속 공백을 정규화한다."""
        assert strip_html_tags("  hello   world  ") == "hello world"

    def test_returns_none_for_none(self) -> None:
        """None 입력에 None을 반환한다."""
        assert strip_html_tags(None) is None

    def test_returns_none_for_empty_after_strip(self) -> None:
        """태그 제거 후 빈 문자열이면 None을 반환한다."""
        assert strip_html_tags("<p></p>") is None
        assert strip_html_tags("<br/>") is None

    def test_complex_html(self) -> None:
        """복잡한 HTML 구조를 처리한다."""
        html = """
        <p>이 약은 <b>두통</b>, <i>치통</i>에 사용합니다.</p>
        <ul>
            <li>1회 1정</li>
            <li>하루 3회</li>
        </ul>
        """
        result = strip_html_tags(html)
        assert "두통" in result
        assert "치통" in result
        assert "1회 1정" in result
        assert "<" not in result


class TestNormalizeWhitespace:
    """normalize_whitespace 함수 테스트."""

    def test_normalizes_spaces(self) -> None:
        """연속 공백을 단일 공백으로 치환한다."""
        assert normalize_whitespace("hello   world") == "hello world"

    def test_normalizes_tabs(self) -> None:
        """탭을 단일 공백으로 치환한다."""
        assert normalize_whitespace("hello\t\tworld") == "hello world"

    def test_strips_leading_trailing(self) -> None:
        """앞뒤 공백을 제거한다."""
        assert normalize_whitespace("  hello  ") == "hello"

    def test_returns_none_for_none(self) -> None:
        """None 입력에 None을 반환한다."""
        assert normalize_whitespace(None) is None

    def test_returns_none_for_whitespace_only(self) -> None:
        """공백만 있으면 None을 반환한다."""
        assert normalize_whitespace("   ") is None


class TestParseMaterialName:
    """parse_material_name 함수 테스트."""

    def test_pipe_separated_format(self) -> None:
        """파이프 구분 형식을 파싱한다."""
        result = parse_material_name("아세트아미노펜|500|mg")
        assert len(result) == 1
        assert result[0]["name"] == "아세트아미노펜"
        assert result[0]["amount"] == "500"
        assert result[0]["unit"] == "mg"

    def test_multiple_ingredients_comma_separated(self) -> None:
        """쉼표로 구분된 복수 성분을 파싱한다."""
        text = "아세트아미노펜|500|mg,카페인|50|mg"
        result = parse_material_name(text)
        assert len(result) == 2
        assert result[0]["name"] == "아세트아미노펜"
        assert result[1]["name"] == "카페인"

    def test_multiple_ingredients_semicolon_separated(self) -> None:
        """세미콜론으로 구분된 복수 성분을 파싱한다."""
        text = "비타민C|500|mg;아연|10|mg"
        result = parse_material_name(text)
        assert len(result) == 2

    def test_pipe_with_empty_fields(self) -> None:
        """비어있는 분량/단위 필드를 None으로 처리한다."""
        result = parse_material_name("아세트아미노펜||")
        assert len(result) == 1
        assert result[0]["name"] == "아세트아미노펜"
        assert result[0]["amount"] is None
        assert result[0]["unit"] is None

    def test_plain_text(self) -> None:
        """파이프 없는 단순 텍스트를 처리한다."""
        result = parse_material_name("아세트아미노펜")
        assert len(result) == 1
        assert result[0]["name"] == "아세트아미노펜"
        assert result[0]["amount"] is None

    def test_empty_returns_empty_list(self) -> None:
        """빈 입력에 빈 리스트를 반환한다."""
        assert parse_material_name(None) == []
        assert parse_material_name("") == []


class TestParseDrugItem:
    """parse_drug_item 함수 테스트."""

    def test_basic_mapping(self) -> None:
        """API 키를 DB 컬럼명으로 올바르게 매핑한다."""
        raw = {
            "itemSeq": "200000001",
            "itemName": "테스트약",
            "entpName": "테스트제약",
            "etcOtcCode": "일반의약품",
            "classNo": "01140",
        }
        result = parse_drug_item(raw)

        assert result["item_seq"] == "200000001"
        assert result["item_name"] == "테스트약"
        assert result["entp_name"] == "테스트제약"
        assert result["etc_otc_code"] == "일반의약품"
        assert result["class_no"] == "01140"

    def test_html_stripping(self) -> None:
        """텍스트 필드의 HTML 태그를 제거한다."""
        raw = {
            "itemSeq": "200000001",
            "itemName": "테스트약",
            "efcyQesitm": "<p>두통, <b>치통</b>에 사용</p>",
            "atpnQesitm": "<p>간장애 환자 <span>주의</span></p>",
        }
        result = parse_drug_item(raw)

        assert result["efcy_qesitm"] == "두통, 치통 에 사용"
        assert "<" not in (result["efcy_qesitm"] or "")
        assert "<" not in (result["atpn_qesitm"] or "")

    def test_ingredients_parsing(self) -> None:
        """material_name을 ingredients로 구조화한다."""
        raw = {
            "itemSeq": "200000001",
            "itemName": "테스트약",
            "materialName": "아세트아미노펜|500|mg,카페인|50|mg",
        }
        result = parse_drug_item(raw)

        assert isinstance(result["ingredients"], list)
        assert len(result["ingredients"]) == 2
        assert result["ingredients"][0]["name"] == "아세트아미노펜"

    def test_none_fields(self) -> None:
        """None 필드를 올바르게 처리한다."""
        raw = {
            "itemSeq": "200000001",
            "itemName": "테스트약",
            "efcyQesitm": None,
            "materialName": None,
        }
        result = parse_drug_item(raw)

        assert result["efcy_qesitm"] is None
        assert result["ingredients"] == []

    def test_empty_string_fields(self) -> None:
        """빈 문자열을 None으로 변환한다."""
        raw = {
            "itemSeq": "200000001",
            "itemName": "테스트약",
            "entpName": "   ",
            "classNo": "",
        }
        result = parse_drug_item(raw)

        assert result["entp_name"] is None
        assert result["class_no"] is None


class TestParseDurItem:
    """parse_dur_item 함수 테스트."""

    def _make_drug_lookup(self) -> dict:
        """테스트용 약물 lookup을 생성한다.

        Returns:
            item_seq -> {id, name} 매핑 딕셔너리.
        """
        return {
            "200000001": {"id": 1, "name": "테스트약A"},
            "200000002": {"id": 2, "name": "테스트약B"},
            "200000003": {"id": 3, "name": "테스트약C"},
        }

    def test_basic_parsing(self) -> None:
        """기본 DUR 항목을 올바르게 파싱한다."""
        raw = {
            "ITEM_SEQ": "200000001",
            "ITEM_NAME": "테스트약A",
            "MIXTURE_ITEM_SEQ": "200000002",
            "MIXTURE_ITEM_NAME": "테스트약B",
            "PROHBT_CONTENT": "병용 시 부작용 위험",
            "REMARK": None,
        }
        lookup = self._make_drug_lookup()
        result = parse_dur_item(raw, lookup)

        assert result is not None
        assert result["severity"] == "danger"
        assert result["source"] == "DUR"
        assert result["evidence_level"] == "official"
        assert result["item_a_type"] == "drug"
        assert result["item_b_type"] == "drug"

    def test_id_ordering(self) -> None:
        """item_a_id < item_b_id 순서로 정렬한다."""
        raw = {
            "ITEM_SEQ": "200000003",  # id=3 (큰 쪽)
            "ITEM_NAME": "테스트약C",
            "MIXTURE_ITEM_SEQ": "200000001",  # id=1 (작은 쪽)
            "MIXTURE_ITEM_NAME": "테스트약A",
            "PROHBT_CONTENT": "병용금기",
            "REMARK": None,
        }
        lookup = self._make_drug_lookup()
        result = parse_dur_item(raw, lookup)

        assert result is not None
        assert result["item_a_id"] == 1  # 작은 ID가 A
        assert result["item_b_id"] == 3  # 큰 ID가 B

    def test_returns_none_for_missing_item_seq(self) -> None:
        """item_seq가 없으면 None을 반환한다."""
        raw = {
            "ITEM_SEQ": None,
            "MIXTURE_ITEM_SEQ": "200000002",
            "PROHBT_CONTENT": "병용금기",
        }
        lookup = self._make_drug_lookup()
        assert parse_dur_item(raw, lookup) is None

    def test_returns_none_for_unknown_drug(self) -> None:
        """DB에 없는 약물이면 None을 반환한다."""
        raw = {
            "ITEM_SEQ": "999999999",  # DB에 없음
            "ITEM_NAME": "미등록약",
            "MIXTURE_ITEM_SEQ": "200000001",
            "MIXTURE_ITEM_NAME": "테스트약A",
            "PROHBT_CONTENT": "병용금기",
        }
        lookup = self._make_drug_lookup()
        assert parse_dur_item(raw, lookup) is None

    def test_source_id_format(self) -> None:
        """source_id가 올바른 형식을 가진다."""
        raw = {
            "ITEM_SEQ": "200000001",
            "MIXTURE_ITEM_SEQ": "200000002",
            "PROHBT_CONTENT": "병용금기",
            "REMARK": None,
        }
        lookup = self._make_drug_lookup()
        result = parse_dur_item(raw, lookup)

        assert result is not None
        assert result["source_id"] == "DUR_200000001_200000002"


class TestBuildInteractionDescription:
    """build_interaction_description 함수 테스트."""

    def test_with_content_only(self) -> None:
        """금기 내용만 있는 경우."""
        result = build_interaction_description("병용 시 위험", None)
        assert result == "병용 시 위험"

    def test_with_content_and_remark(self) -> None:
        """금기 내용 + 비고가 있는 경우."""
        result = build_interaction_description("병용 시 위험", "전문가 상담 필요")
        assert "병용 시 위험" in result
        assert "[비고]" in result
        assert "전문가 상담 필요" in result

    def test_with_html_content(self) -> None:
        """HTML이 포함된 금기 내용을 정리한다."""
        result = build_interaction_description("<p>병용 시 위험</p>", None)
        assert "<" not in result
        assert "병용 시 위험" in result

    def test_with_none_both(self) -> None:
        """둘 다 None이면 기본 메시지를 반환한다."""
        result = build_interaction_description(None, None)
        assert "DUR 병용금기" in result
