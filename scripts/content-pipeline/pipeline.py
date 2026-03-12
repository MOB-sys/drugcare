"""콘텐츠 파이프라인 메인 오케스트레이터.

사용법:
    python pipeline.py --research          # PubMed 논문 수집 + 요약
    python pipeline.py --news              # 안전 경고 수집 + 요약
    python pipeline.py --all               # 전체 실행
    python pipeline.py --validate-only     # 기존 콘텐츠 검증만
    python pipeline.py --dry-run --all     # 실제 파일 생성 없이 테스트
"""

import argparse
import sys
import time
from pathlib import Path

from ai_summarizer import summarize_alert, summarize_research
from config import CONTENT_DIR, PUBMED_QUERIES
from content_validator import validate
from markdown_writer import slugify, write_news, write_research
from pubmed_fetcher import search_and_fetch
from safety_alert_fetcher import fetch_all_alerts


def run_research_pipeline(dry_run: bool = False) -> dict:
    """PubMed 논문 검색 → AI 요약 → Markdown 생성."""
    stats = {"searched": 0, "summarized": 0, "written": 0, "skipped": 0, "errors": 0}

    for query in PUBMED_QUERIES:
        print(f"\n🔍 검색: {query[:60]}...")
        articles = search_and_fetch(query)
        stats["searched"] += len(articles)
        print(f"  → {len(articles)}건 발견")

        for article in articles:
            print(f"\n  📄 [{article.pmid}] {article.title[:60]}...")

            # AI 요약
            summary = summarize_research(article)
            if not summary:
                stats["errors"] += 1
                continue
            stats["summarized"] += 1

            # 콘텐츠 검증
            content = summary.get("content", "")
            title = summary.get("title", "")
            passed, warnings = validate(content, title)

            if warnings:
                for w in warnings:
                    print(f"    ⚠️ {w}")

            if not passed:
                print(f"    ❌ 검증 실패, 건너뜀")
                stats["skipped"] += 1
                continue

            if dry_run:
                print(f"    🏷️ [DRY RUN] {title}")
                stats["written"] += 1
                continue

            # Markdown 파일 생성
            slug = slugify(f"{article.pmid}-{title}")
            filepath = write_research(
                slug=slug,
                title=title,
                description=summary.get("description", ""),
                content=content,
                tags=summary.get("tags", []),
                pmid=article.pmid,
                doi=article.doi,
                authors=article.authors,
                journal=article.journal,
                evidence_level=summary.get("evidence_level", "moderate"),
                review_status="review",  # 자동 생성은 review 상태
            )

            if filepath:
                print(f"    ✅ 생성: {filepath}")
                stats["written"] += 1
            else:
                print(f"    ⏭️ 이미 존재, 건너뜀")
                stats["skipped"] += 1

        time.sleep(1)  # 쿼리 간 딜레이

    return stats


def run_news_pipeline(dry_run: bool = False) -> dict:
    """안전 경고 수집 → AI 요약 → Markdown 생성."""
    stats = {"fetched": 0, "summarized": 0, "written": 0, "skipped": 0, "errors": 0}

    print("\n📡 안전 경고 수집 중...")
    alerts = fetch_all_alerts(max_per_source=10)
    stats["fetched"] = len(alerts)
    print(f"  → {len(alerts)}건 수집")

    for alert in alerts:
        print(f"\n  📰 [{alert.source}] {alert.title[:60]}...")

        # AI 요약
        summary = summarize_alert(alert.title, alert.content, alert.source)
        if not summary:
            stats["errors"] += 1
            continue
        stats["summarized"] += 1

        # 콘텐츠 검증
        content = summary.get("content", "")
        title = summary.get("title", "")
        passed, warnings = validate(content, title)

        if warnings:
            for w in warnings:
                print(f"    ⚠️ {w}")

        if not passed:
            print(f"    ❌ 검증 실패, 건너뜀")
            stats["skipped"] += 1
            continue

        if dry_run:
            print(f"    🏷️ [DRY RUN] {title}")
            stats["written"] += 1
            continue

        # Markdown 파일 생성
        slug = slugify(title)
        filepath = write_news(
            slug=slug,
            title=title,
            description=summary.get("description", ""),
            content=content,
            tags=summary.get("tags", []),
            source=alert.source,
            source_url=alert.source_url,
            severity=summary.get("severity", alert.severity),
            review_status="review",
        )

        if filepath:
            print(f"    ✅ 생성: {filepath}")
            stats["written"] += 1
        else:
            print(f"    ⏭️ 이미 존재, 건너뜀")
            stats["skipped"] += 1

    return stats


def run_validation() -> dict:
    """기존 콘텐츠 파일 일괄 검증."""
    stats = {"checked": 0, "passed": 0, "failed": 0}

    for content_type in ["tips", "news", "research"]:
        content_dir = CONTENT_DIR / content_type
        if not content_dir.exists():
            continue

        for md_file in sorted(content_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")

            # frontmatter 분리
            if text.startswith("---"):
                parts = text.split("---", 2)
                body = parts[2] if len(parts) > 2 else ""
            else:
                body = text

            passed, warnings = validate(body, md_file.stem)
            stats["checked"] += 1

            if passed:
                stats["passed"] += 1
            else:
                stats["failed"] += 1
                print(f"  ❌ {md_file.name}:")
                for w in warnings:
                    print(f"     - {w}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="약먹어 콘텐츠 파이프라인")
    parser.add_argument("--research", action="store_true", help="PubMed 논문 파이프라인")
    parser.add_argument("--news", action="store_true", help="안전 경고 파이프라인")
    parser.add_argument("--all", action="store_true", help="전체 파이프라인")
    parser.add_argument("--validate-only", action="store_true", help="기존 콘텐츠 검증만")
    parser.add_argument("--dry-run", action="store_true", help="파일 생성 없이 테스트")

    args = parser.parse_args()

    if not any([args.research, args.news, args.all, args.validate_only]):
        parser.print_help()
        sys.exit(1)

    print("=" * 60)
    print("🏥 약먹어 콘텐츠 파이프라인")
    print("=" * 60)

    if args.dry_run:
        print("🧪 DRY RUN 모드 — 파일을 생성하지 않습니다\n")

    # 검증
    if args.validate_only or args.all:
        print("\n📋 기존 콘텐츠 검증")
        print("-" * 40)
        v_stats = run_validation()
        print(f"\n검증 완료: {v_stats['checked']}건 검사, "
              f"{v_stats['passed']}건 통과, {v_stats['failed']}건 실패")

        if args.validate_only:
            sys.exit(0 if v_stats["failed"] == 0 else 1)

    # 연구 논문
    if args.research or args.all:
        print("\n📚 PubMed 연구 논문 파이프라인")
        print("-" * 40)
        r_stats = run_research_pipeline(dry_run=args.dry_run)
        print(f"\n연구 완료: 검색 {r_stats['searched']}건, "
              f"요약 {r_stats['summarized']}건, "
              f"생성 {r_stats['written']}건, "
              f"건너뜀 {r_stats['skipped']}건, "
              f"에러 {r_stats['errors']}건")

    # 안전 경고
    if args.news or args.all:
        print("\n📰 안전 경고 파이프라인")
        print("-" * 40)
        n_stats = run_news_pipeline(dry_run=args.dry_run)
        print(f"\n뉴스 완료: 수집 {n_stats['fetched']}건, "
              f"요약 {n_stats['summarized']}건, "
              f"생성 {n_stats['written']}건, "
              f"건너뜀 {n_stats['skipped']}건, "
              f"에러 {n_stats['errors']}건")

    print("\n" + "=" * 60)
    print("✅ 파이프라인 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
