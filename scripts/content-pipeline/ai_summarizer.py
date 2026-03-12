"""AI 기반 논문/경고 → 한국어 콘텐츠 요약.

OPENAI_API_KEY가 없으면 템플릿 기반 로컬 요약으로 폴백한다.
"""

import json
import re

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment,misc]

from config import AI_MAX_TOKENS, AI_MODEL, OPENAI_API_KEY, REQUIRED_DISCLAIMER
from pubmed_fetcher import PubMedArticle

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OpenAI else None

RESEARCH_PROMPT = """당신은 약물 안전 정보 전문 에디터입니다.
다음 영문 논문 초록을 일반인이 이해할 수 있는 한국어 건강 콘텐츠로 변환하세요.

## 출력 형식 (JSON)
{{
  "title": "한국어 제목 (30자 이내)",
  "description": "한 줄 요약 (80자 이내)",
  "content": "마크다운 본문 (## 연구 요약, ## 핵심 결과, ## 일반인을 위한 해석, ### 실천 사항 섹션 포함)",
  "tags": ["태그1", "태그2", "태그3"],
  "evidence_level": "high|moderate|low"
}}

## 규칙
- 300~800자 분량의 content
- "~할 수 있습니다", "~의 가능성이 있습니다" 등 단정 회피
- 의학적 진단/치료 문구 금지 ("암 예방", "완벽하게 치료" 등 금지)
- 마지막에 반드시 면책조항 포함: "> 이 정보는 의학 논문의 요약이며, 의사/약사의 전문적 판단을 대체하지 않습니다. (PMID: {{pmid}})"
- 출처 PMID 명시
- JSON만 출력, 다른 텍스트 없이

## 논문 정보
제목: {title}
저널: {journal}
저자: {authors}
PMID: {pmid}
초록: {abstract}
"""

NEWS_PROMPT = """당신은 약물 안전 정보 전문 에디터입니다.
다음 안전 경고 정보를 일반인이 이해할 수 있는 한국어 뉴스 기사로 변환하세요.

## 출력 형식 (JSON)
{{
  "title": "한국어 제목 (40자 이내)",
  "description": "한 줄 요약 (80자 이내)",
  "content": "마크다운 본문 (## 주요 내용, ## 영향받는 약물, ## 권장 사항 섹션 포함)",
  "tags": ["태그1", "태그2", "태그3"],
  "severity": "info|warning|danger"
}}

## 규칙
- 200~600자 분량의 content
- 단정적 표현 회피
- 마지막에 면책조항 포함
- JSON만 출력

## 원본 정보
제목: {title}
출처: {source}
내용: {content}
"""


def _truncate(text: str, max_len: int) -> str:
    """문장 단위로 잘라서 max_len 이내로."""
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(". ", 1)[0]
    return cut + "." if not cut.endswith(".") else cut


def _extract_tags_from_mesh(article: PubMedArticle) -> list[str]:
    """MeSH 용어에서 태그 추출."""
    tag_map = {
        "Drug Interactions": "약물 상호작용",
        "Dietary Supplements": "영양제",
        "Herb-Drug Interactions": "한약재 상호작용",
        "Food-Drug Interactions": "음식-약물 상호작용",
        "Polypharmacy": "다제복용",
        "Pregnancy": "임산부",
        "Aged": "고령자",
        "Adverse Effects": "부작용",
        "Drug Safety": "약물 안전",
        "Vitamins": "비타민",
        "Anti-Bacterial Agents": "항생제",
        "Antineoplastic Agents": "항암제",
        "Anticoagulants": "항응고제",
        "Probiotics": "유산균",
    }
    tags = []
    for mesh in article.mesh_terms:
        if mesh in tag_map:
            tags.append(tag_map[mesh])
    if not tags:
        tags = ["약물 연구", "복약 안전"]
    return tags[:5]


def local_summarize_research(article: PubMedArticle) -> dict:
    """AI 없이 템플릿 기반으로 연구 요약 생성."""
    abstract = _truncate(article.abstract, 1500)
    authors_str = ", ".join(article.authors[:3])
    if len(article.authors) > 3:
        authors_str += " 외"

    title = article.title
    if len(title) > 60:
        title = title[:57] + "..."

    description = f"{article.journal}에 발표된 연구 — {title[:50]}"
    if len(description) > 80:
        description = description[:77] + "..."

    tags = _extract_tags_from_mesh(article)

    content = f"""## 연구 요약

**{article.title}**

{article.journal} 학술지에 발표된 이 연구는 {authors_str} 연구팀이 수행하였습니다.

## 핵심 내용

{abstract}

## 일반인을 위한 해석

이 연구는 약물 또는 영양제의 안전한 사용에 관한 과학적 근거를 제공할 수 있습니다. 다만, 개별 연구 결과만으로 일반화하기는 어려우며, 추가적인 연구가 필요할 수 있습니다.

### 실천 사항

- 현재 복용 중인 약물이나 영양제에 대해 궁금한 점이 있다면 담당 의사 또는 약사와 상담하시기 바랍니다
- 약물이나 영양제의 용법·용량을 임의로 변경하지 마세요
- 이상 반응이 나타나면 즉시 전문가에게 문의하세요

> {REQUIRED_DISCLAIMER} (PMID: {article.pmid})"""

    # 근거 수준 추정
    abstract_lower = article.abstract.lower()
    if any(kw in abstract_lower for kw in ["meta-analysis", "systematic review", "cochrane"]):
        evidence = "high"
    elif any(kw in abstract_lower for kw in ["randomized", "rct", "controlled trial", "double-blind"]):
        evidence = "high"
    elif any(kw in abstract_lower for kw in ["cohort", "prospective", "retrospective"]):
        evidence = "moderate"
    else:
        evidence = "moderate"

    return {
        "title": title,
        "description": description,
        "content": content,
        "tags": tags,
        "evidence_level": evidence,
    }


def local_summarize_alert(title: str, content: str, source: str) -> dict:
    """AI 없이 템플릿 기반으로 안전 경고 요약 생성."""
    source_label = {"mfds": "식약처", "fda": "미국 FDA", "ema": "유럽 EMA"}.get(source, source)

    # 심각도 추정
    severity = "info"
    combined = (title + " " + content).lower()
    if any(kw in combined for kw in ["recall", "회수", "class i", "판매중지", "death", "사망"]):
        severity = "danger"
    elif any(kw in combined for kw in ["warning", "주의", "경고", "class ii", "변경"]):
        severity = "warning"

    body = f"""## 주요 내용

{source_label}에서 발표한 의약품 안전 정보입니다.

{content[:800]}

## 권장 사항

- 해당 의약품을 복용 중인 경우, 담당 의사 또는 약사와 상담하시기 바랍니다
- 이상 반응이 나타나면 즉시 의료기관을 방문하세요
- 임의로 약물 복용을 중단하지 마세요

> {REQUIRED_DISCLAIMER}"""

    if len(title) > 40:
        title = title[:37] + "..."

    description = f"{source_label} 안전 정보 — {title[:40]}"
    if len(description) > 80:
        description = description[:77] + "..."

    return {
        "title": title,
        "description": description,
        "content": body,
        "tags": ["의약품 안전", source_label, "안전 경고"],
        "severity": severity,
    }


def summarize_research(article: PubMedArticle) -> dict | None:
    """PubMed 논문을 한국어 연구 요약으로 변환. AI 없으면 로컬 폴백."""
    if not client:
        print("  ℹ️ OPENAI_API_KEY 미설정 → 로컬 요약 사용")
        return local_summarize_research(article)

    prompt = RESEARCH_PROMPT.format(
        title=article.title,
        journal=article.journal,
        authors=", ".join(article.authors[:5]),
        pmid=article.pmid,
        abstract=article.abstract[:3000],
    )

    try:
        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=AI_MAX_TOKENS,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        if not content:
            return None
        return json.loads(content)
    except Exception as e:
        print(f"  ❌ AI 요약 실패 [{article.pmid}]: {e}")
        return None


def summarize_alert(title: str, content: str, source: str) -> dict | None:
    """안전 경고를 한국어 뉴스로 변환. AI 없으면 로컬 폴백."""
    if not client:
        print("  ℹ️ OPENAI_API_KEY 미설정 → 로컬 요약 사용")
        return local_summarize_alert(title, content, source)

    prompt = NEWS_PROMPT.format(title=title, source=source, content=content[:3000])

    try:
        resp = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=AI_MAX_TOKENS,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        result = resp.choices[0].message.content
        if not result:
            return None
        return json.loads(result)
    except Exception as e:
        print(f"  ❌ AI 요약 실패: {e}")
        return None
