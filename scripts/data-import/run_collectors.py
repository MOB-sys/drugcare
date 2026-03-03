"""데이터 수집 오케스트레이터 — 공공데이터 API 수집 파이프라인 실행.

사용법:
    # 전체 수집 (e약은요 → 허가정보 → DUR 순서)
    python -m scripts.data-import.run_collectors --all

    # 개별 수집
    python -m scripts.data-import.run_collectors --edrug
    python -m scripts.data-import.run_collectors --permission
    python -m scripts.data-import.run_collectors --dur

    # 페이지 제한 (테스트용)
    python -m scripts.data-import.run_collectors --all --max-pages 5
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가 (스크립트 직접 실행 시)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.core.database import async_session_factory
from src.data.scrapers.dur_interaction_collector import DURInteractionCollector
from src.data.scrapers.dur_safety_collector import DURSafetyCollector
from src.data.scrapers.drug_permission_collector import DrugPermissionCollector
from src.data.scrapers.edrug_collector import EDrugCollector
from src.data.scrapers.supplement_collector import SupplementCollector

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("data_collector")


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다.

    Returns:
        파싱된 인자 네임스페이스.
    """
    parser = argparse.ArgumentParser(
        description="약먹어 데이터 수집 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
수집 순서 (--all):
  1. e약은요 API → drugs 테이블 (의약품 기본정보)
  2. 허가정보 API → drugs.ingredients 보강 (성분 상세)
  3. DUR API    → interactions 테이블 (병용금기)

예시:
  python -m scripts.data-import.run_collectors --all
  python -m scripts.data-import.run_collectors --edrug --max-pages 3
  python -m scripts.data-import.run_collectors --dur
        """,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="전체 수집 실행 (e약은요 → 허가정보 → DUR)",
    )
    parser.add_argument(
        "--edrug",
        action="store_true",
        help="e약은요 API 수집 (의약품 기본정보)",
    )
    parser.add_argument(
        "--permission",
        action="store_true",
        help="허가정보 API 수집 (성분 상세 보강)",
    )
    parser.add_argument(
        "--dur",
        action="store_true",
        help="DUR 병용금기 API 수집 (상호작용)",
    )
    parser.add_argument(
        "--dur-safety",
        action="store_true",
        help="DUR 안전성 API 수집 (임부금기/노인주의/용량주의/투여기간주의/효능군중복)",
    )
    parser.add_argument(
        "--supplements",
        action="store_true",
        help="건강기능식품 API 수집 (식약처 C003)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="최대 수집 페이지 수 (테스트용, 기본: 전량)",
    )

    args = parser.parse_args()

    # 인자가 하나도 없으면 도움말 출력
    if not (args.all or args.edrug or args.permission or args.dur or args.dur_safety or args.supplements):
        parser.print_help()
        sys.exit(1)

    return args


async def run_edrug_collector(max_pages: int | None = None) -> dict[str, int]:
    """e약은요 수집기를 실행한다.

    Args:
        max_pages: 최대 수집 페이지 수.

    Returns:
        수집 통계 딕셔너리.
    """
    logger.info("=" * 60)
    logger.info("e약은요 수집기 시작")
    logger.info("=" * 60)

    collector = EDrugCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


async def run_permission_collector(max_pages: int | None = None) -> dict[str, int]:
    """허가정보 수집기를 실행한다.

    Args:
        max_pages: 최대 수집 페이지 수.

    Returns:
        수집 통계 딕셔너리.
    """
    logger.info("=" * 60)
    logger.info("허가정보 수집기 시작")
    logger.info("=" * 60)

    collector = DrugPermissionCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


async def run_dur_collector(max_pages: int | None = None) -> dict[str, int]:
    """DUR 병용금기 수집기를 실행한다.

    Args:
        max_pages: 최대 수집 페이지 수.

    Returns:
        수집 통계 딕셔너리.
    """
    logger.info("=" * 60)
    logger.info("DUR 병용금기 수집기 시작")
    logger.info("=" * 60)

    collector = DURInteractionCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


async def run_dur_safety_collector(max_pages: int | None = None) -> dict[str, int]:
    """DUR 안전성 수집기를 실행한다.

    Args:
        max_pages: API당 최대 수집 페이지 수.

    Returns:
        수집 통계 딕셔너리.
    """
    logger.info("=" * 60)
    logger.info("DUR 안전성 수집기 시작")
    logger.info("=" * 60)

    collector = DURSafetyCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


async def run_supplement_collector(max_pages: int | None = None) -> dict[str, int]:
    """건강기능식품 수집기를 실행한다.

    Args:
        max_pages: 최대 수집 배치 수.

    Returns:
        수집 통계 딕셔너리.
    """
    logger.info("=" * 60)
    logger.info("건강기능식품 수집기 시작")
    logger.info("=" * 60)

    collector = SupplementCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


def print_summary(all_stats: dict[str, dict[str, int]], elapsed_sec: float) -> None:
    """수집 결과 요약을 출력한다.

    Args:
        all_stats: 수집기별 통계 딕셔너리.
        elapsed_sec: 전체 소요 시간(초).
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("수집 결과 요약")
    logger.info("=" * 60)
    logger.info("완료 시각: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("소요 시간: %.1f초 (%.1f분)", elapsed_sec, elapsed_sec / 60)
    logger.info("-" * 60)

    for collector_name, stats in all_stats.items():
        logger.info("[%s]", collector_name)
        for key, value in stats.items():
            logger.info("  %-12s: %d", key, value)
        logger.info("")

    logger.info("=" * 60)


async def main() -> None:
    """메인 실행 함수. CLI 인자에 따라 수집기를 순차 실행한다."""
    args = parse_args()
    max_pages = args.max_pages

    start_time = time.time()
    all_stats: dict[str, dict[str, int]] = {}

    logger.info("약먹어 데이터 수집 파이프라인 시작")
    logger.info("시작 시각: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if max_pages is not None:
        logger.info("페이지 제한: %d페이지", max_pages)

    try:
        # 1. e약은요 수집
        if args.all or args.edrug:
            stats = await run_edrug_collector(max_pages)
            all_stats["e약은요"] = stats

        # 2. 허가정보 수집 (e약은요 이후에 실행해야 drugs 데이터 참조 가능)
        if args.all or args.permission:
            stats = await run_permission_collector(max_pages)
            all_stats["허가정보"] = stats

        # 3. DUR 병용금기 수집 (drugs 데이터가 있어야 매칭 가능)
        if args.all or args.dur:
            stats = await run_dur_collector(max_pages)
            all_stats["DUR 병용금기"] = stats

        # 4. DUR 안전성 수집 (임부금기/노인주의/용량주의/투여기간주의/효능군중복)
        if args.all or args.dur_safety:
            stats = await run_dur_safety_collector(max_pages)
            all_stats["DUR 안전성"] = stats

        # 5. 건강기능식품 수집
        if args.all or args.supplements:
            stats = await run_supplement_collector(max_pages)
            all_stats["건강기능식품"] = stats

    except KeyboardInterrupt:
        logger.warning("사용자에 의해 수집 중단")
    except Exception as e:
        logger.error("수집 중 오류 발생: %s", e, exc_info=True)
        raise
    finally:
        elapsed = time.time() - start_time
        print_summary(all_stats, elapsed)


if __name__ == "__main__":
    asyncio.run(main())
