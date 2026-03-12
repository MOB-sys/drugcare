"""Markdown + frontmatter 파일 생성."""

import os
import re
from datetime import date

from config import NEWS_DIR, RESEARCH_DIR, TIPS_DIR


def slugify(text: str) -> str:
    """텍스트를 URL-safe slug로 변환."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-")


def _quote(val: str) -> str:
    """YAML 안전 문자열."""
    return f'"{val}"'


def write_research(
    slug: str,
    title: str,
    description: str,
    content: str,
    tags: list[str],
    pmid: str = "",
    doi: str = "",
    authors: list[str] | None = None,
    journal: str = "",
    evidence_level: str = "moderate",
    review_status: str = "draft",
) -> str:
    """연구 요약 Markdown 파일 생성."""
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    filepath = RESEARCH_DIR / f"{slug}.md"

    # 중복 체크
    if filepath.exists():
        return ""

    tags_str = ", ".join(f'"{t}"' for t in tags)
    authors_str = ", ".join(f'"{a}"' for a in (authors or []))
    today = date.today().isoformat()

    frontmatter = f"""---
slug: {_quote(slug)}
title: {_quote(title)}
description: {_quote(description)}
tags: [{tags_str}]
category: "interaction"
source: "pubmed"
pubmedId: {_quote(pmid)}
doi: {_quote(doi)}
authors: [{authors_str}]
journal: {_quote(journal)}
publishedAt: {_quote(today)}
reviewStatus: {_quote(review_status)}
relatedIngredients: []
evidenceLevel: {_quote(evidence_level)}
---
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + "\n" + content.strip() + "\n")

    return str(filepath)


def write_news(
    slug: str,
    title: str,
    description: str,
    content: str,
    tags: list[str],
    source: str = "mfds",
    source_url: str = "",
    severity: str = "info",
    review_status: str = "draft",
) -> str:
    """뉴스/안전 경고 Markdown 파일 생성."""
    os.makedirs(NEWS_DIR, exist_ok=True)
    filepath = NEWS_DIR / f"{slug}.md"

    if filepath.exists():
        return ""

    tags_str = ", ".join(f'"{t}"' for t in tags)
    today = date.today().isoformat()

    frontmatter = f"""---
slug: {_quote(slug)}
title: {_quote(title)}
description: {_quote(description)}
tags: [{tags_str}]
category: "safety-alert"
source: {_quote(source)}
sourceUrl: {_quote(source_url)}
publishedAt: {_quote(today)}
reviewStatus: {_quote(review_status)}
severity: {_quote(severity)}
relatedDrugs: []
---
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + "\n" + content.strip() + "\n")

    return str(filepath)
