"""콘텐츠 파이프라인 설정."""

import os
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
TIPS_DIR = CONTENT_DIR / "tips"
NEWS_DIR = CONTENT_DIR / "news"
RESEARCH_DIR = CONTENT_DIR / "research"

# PubMed E-utilities
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")  # 무료 등록
PUBMED_MAX_RESULTS = 20
PUBMED_RATE_LIMIT = 3  # req/sec (API 키 없을 때)

# 검색 쿼리 (로테이션)
PUBMED_QUERIES = [
    '"drug interactions"[MeSH] AND "dietary supplements"[MeSH] AND "last 30 days"[dp]',
    '"herb-drug interactions"[MeSH] AND "last 30 days"[dp]',
    '"food-drug interactions"[MeSH] AND "last 30 days"[dp]',
    '"drug safety"[MeSH] AND "polypharmacy"[MeSH] AND "last 30 days"[dp]',
    '"pregnancy"[MeSH] AND "drug-related side effects"[MeSH] AND "last 90 days"[dp]',
    '"aged"[MeSH] AND "drug interactions"[MeSH] AND "last 90 days"[dp]',
    '"dietary supplements"[MeSH] AND "adverse effects"[MeSH] AND "last 30 days"[dp]',
]

# AI 요약
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = "gpt-4o"
AI_MAX_TOKENS = 1500

# 식약처
MFDS_RSS_URL = "https://www.mfds.go.kr/brd/m_99/list.do"

# FDA openFDA
FDA_API_BASE = "https://api.fda.gov/drug"

# 콘텐츠 검증
BANNED_EXPRESSIONS = [
    "완벽하게 치료",
    "100% 안전",
    "부작용 없",
    "기적의 약",
    "암을 치료",
    "확실한 효과",
    "만병통치",
    "즉시 효과",
    "완치",
    "기적적",
]

REQUIRED_DISCLAIMER = "의사/약사의 전문적 판단을 대체하지 않습니다"
