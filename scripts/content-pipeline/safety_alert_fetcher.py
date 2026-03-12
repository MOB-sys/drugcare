"""식약처 + FDA openFDA 안전 경고 수집."""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import FDA_API_BASE, MFDS_RSS_URL


@dataclass
class SafetyAlert:
    """안전 경고 메타데이터."""
    title: str
    content: str
    source: str  # "mfds" | "fda"
    source_url: str = ""
    severity: str = "info"  # "info" | "warning" | "danger"


def fetch_mfds_alerts(max_results: int = 10) -> list[SafetyAlert]:
    """식약처 의약품 안전 정보 페이지 스크래핑."""
    alerts: list[SafetyAlert] = []

    try:
        params = {"pageIndex": 1, "searchCnd": 1, "searchWrd": ""}
        url = f"{MFDS_RSS_URL}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "YakMeogeo-Bot/1.0"})

        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # 제목 추출 (간단 패턴)
        title_pattern = re.compile(
            r'<td class="ta_l">.*?<a[^>]*>(.*?)</a>', re.DOTALL
        )
        matches = title_pattern.findall(html)

        for title_raw in matches[:max_results]:
            title = re.sub(r"<[^>]+>", "", title_raw).strip()
            title = re.sub(r"\s+", " ", title)
            if not title:
                continue

            severity = "info"
            if any(kw in title for kw in ["회수", "판매중지", "긴급"]):
                severity = "danger"
            elif any(kw in title for kw in ["주의", "경고", "변경"]):
                severity = "warning"

            alerts.append(SafetyAlert(
                title=title,
                content=title,  # 상세 내용은 AI 요약 시 보충
                source="mfds",
                source_url=MFDS_RSS_URL,
                severity=severity,
            ))

    except Exception as e:
        print(f"  ❌ 식약처 수집 실패: {e}")

    return alerts


def fetch_fda_alerts(max_results: int = 10) -> list[SafetyAlert]:
    """FDA openFDA drug enforcement/event API 조회."""
    alerts: list[SafetyAlert] = []

    try:
        params = {
            "search": 'report_date:[20240101+TO+20261231]',
            "limit": max_results,
            "sort": "report_date:desc",
        }
        url = f"{FDA_API_BASE}/enforcement.json?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "YakMeogeo-Bot/1.0"})

        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for result in data.get("results", []):
            reason = result.get("reason_for_recall", "")
            product = result.get("product_description", "")
            classification = result.get("classification", "")
            status = result.get("status", "")

            title = reason[:100] if reason else product[:100]
            if not title:
                continue

            content = f"제품: {product}\n사유: {reason}\n상태: {status}"

            severity = "info"
            if classification == "Class I":
                severity = "danger"
            elif classification == "Class II":
                severity = "warning"

            alerts.append(SafetyAlert(
                title=title,
                content=content,
                source="fda",
                source_url=f"https://api.fda.gov/drug/enforcement.json",
                severity=severity,
            ))

    except Exception as e:
        print(f"  ❌ FDA 수집 실패: {e}")

    return alerts


def fetch_all_alerts(max_per_source: int = 10) -> list[SafetyAlert]:
    """모든 소스에서 안전 경고 수집."""
    alerts: list[SafetyAlert] = []
    alerts.extend(fetch_mfds_alerts(max_per_source))
    alerts.extend(fetch_fda_alerts(max_per_source))
    return alerts


if __name__ == "__main__":
    print("=== 식약처 ===")
    for a in fetch_mfds_alerts(3):
        print(f"  [{a.severity}] {a.title}")

    print("\n=== FDA ===")
    for a in fetch_fda_alerts(3):
        print(f"  [{a.severity}] {a.title[:80]}")
