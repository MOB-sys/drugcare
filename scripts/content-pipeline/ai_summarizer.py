"""AI 기반 논문/경고 → 한국어 콘텐츠 요약."""

import json
from openai import OpenAI

from config import AI_MAX_TOKENS, AI_MODEL, OPENAI_API_KEY
from pubmed_fetcher import PubMedArticle

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

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


def summarize_research(article: PubMedArticle) -> dict | None:
    """PubMed 논문을 한국어 연구 요약으로 변환."""
    if not client:
        print("  ⚠️ OPENAI_API_KEY 미설정, 건너뜀")
        return None

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
    """안전 경고를 한국어 뉴스로 변환."""
    if not client:
        print("  ⚠️ OPENAI_API_KEY 미설정, 건너뜀")
        return None

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
