"""PubMed E-utilities 연동 — 최신 약물 안전 논문 검색."""

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urlencode
from urllib.request import urlopen

from config import PUBMED_API_KEY, PUBMED_BASE_URL, PUBMED_MAX_RESULTS, PUBMED_RATE_LIMIT


@dataclass
class PubMedArticle:
    """PubMed 논문 메타데이터."""
    pmid: str
    title: str
    abstract: str
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    doi: str = ""
    pub_date: str = ""
    mesh_terms: list[str] = field(default_factory=list)


def search(query: str, max_results: int = PUBMED_MAX_RESULTS) -> list[str]:
    """PubMed 검색 → PMID 목록 반환."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "date",
        "retmode": "xml",
    }
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY

    url = f"{PUBMED_BASE_URL}/esearch.fcgi?{urlencode(params)}"
    with urlopen(url, timeout=30) as resp:
        tree = ET.parse(resp)

    ids = [el.text for el in tree.findall(".//Id") if el.text]
    return ids


def fetch_articles(pmids: list[str]) -> list[PubMedArticle]:
    """PMID 목록으로 논문 상세 정보 조회."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY

    url = f"{PUBMED_BASE_URL}/efetch.fcgi?{urlencode(params)}"
    time.sleep(1.0 / PUBMED_RATE_LIMIT)

    with urlopen(url, timeout=60) as resp:
        tree = ET.parse(resp)

    articles = []
    for article_el in tree.findall(".//PubmedArticle"):
        medline = article_el.find(".//MedlineCitation")
        if medline is None:
            continue

        pmid_el = medline.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None and pmid_el.text else ""

        title_el = medline.find(".//ArticleTitle")
        title = title_el.text if title_el is not None and title_el.text else ""

        abstract_parts = []
        for ab_el in medline.findall(".//AbstractText"):
            if ab_el.text:
                label = ab_el.get("Label", "")
                prefix = f"{label}: " if label else ""
                abstract_parts.append(prefix + ab_el.text)
        abstract = " ".join(abstract_parts)

        authors = []
        for author_el in medline.findall(".//Author"):
            last = author_el.findtext("LastName", "")
            initials = author_el.findtext("Initials", "")
            if last:
                authors.append(f"{last} {initials}".strip())

        journal = medline.findtext(".//Journal/Title", "")

        doi = ""
        for id_el in article_el.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi" and id_el.text:
                doi = id_el.text
                break

        pub_date_el = medline.find(".//PubDate")
        pub_date = ""
        if pub_date_el is not None:
            year = pub_date_el.findtext("Year", "")
            month = pub_date_el.findtext("Month", "01")
            day = pub_date_el.findtext("Day", "01")
            pub_date = f"{year}-{month}-{day}"

        mesh_terms = [
            m.findtext("DescriptorName", "")
            for m in medline.findall(".//MeshHeading")
            if m.findtext("DescriptorName")
        ]

        if title and abstract:
            articles.append(PubMedArticle(
                pmid=pmid, title=title, abstract=abstract,
                authors=authors[:5], journal=journal, doi=doi,
                pub_date=pub_date, mesh_terms=mesh_terms,
            ))

    return articles


def search_and_fetch(query: str, max_results: int = PUBMED_MAX_RESULTS) -> list[PubMedArticle]:
    """검색 + 상세 조회 원스텝."""
    pmids = search(query, max_results)
    if not pmids:
        return []
    time.sleep(1.0 / PUBMED_RATE_LIMIT)
    return fetch_articles(pmids)


if __name__ == "__main__":
    from config import PUBMED_QUERIES
    query = PUBMED_QUERIES[0]
    print(f"검색: {query}")
    articles = search_and_fetch(query, 5)
    for a in articles:
        print(f"  [{a.pmid}] {a.title[:80]}...")
        print(f"    Journal: {a.journal}")
        print(f"    Authors: {', '.join(a.authors[:3])}")
        print()
