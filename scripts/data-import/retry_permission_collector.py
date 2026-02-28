"""허가정보 API 자동 재시도 수집기.

API 서버(DrugPrdtPrmsnInfoService05)가 500 에러로 다운된 상태에서
복구를 감지하여 자동으로 drugs.ingredients 데이터를 수집한다.

사용법:
    # 1회 시도 후 종료 (cron용)
    python -m scripts.data-import.retry_permission_collector --once

    # 30분 간격 헬스체크 (기본)
    python -m scripts.data-import.retry_permission_collector

    # 5분 간격, 백그라운드
    nohup python -m scripts.data-import.retry_permission_collector --interval 5 &

    # 로그 모니터링
    tail -f /tmp/permission_retry.log
"""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.backend.core.config import get_settings
from src.backend.core.database import async_session_factory
from src.data.scrapers.drug_permission_collector import (
    PERMISSION_API_URL,
    DrugPermissionCollector,
)

logger = logging.getLogger("retry_permission")

HEALTHCHECK_TIMEOUT_SEC = 15


def setup_logging(log_file: str) -> None:
    """stdout + 파일 듀얼 로깅을 설정한다.

    Args:
        log_file: 로그 파일 경로.
    """
    fmt = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # stdout 핸들러
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(stdout_handler)

    # 파일 핸들러
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(file_handler)


async def check_api_health() -> bool:
    """허가정보 API에 1건 요청하여 정상 응답 여부를 확인한다.

    Returns:
        API가 정상이면 True.
    """
    settings = get_settings()
    params = {
        "serviceKey": settings.DATA_GO_KR_SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "1",
        "type": "json",
    }

    try:
        async with httpx.AsyncClient(timeout=HEALTHCHECK_TIMEOUT_SEC) as client:
            response = await client.get(PERMISSION_API_URL, params=params)
            response.raise_for_status()

            data = response.json()
            body = data.get("body", {})
            total_count = int(body.get("totalCount", 0))

            if total_count > 0:
                logger.info(
                    "API 헬스체크 성공 — HTTP %d, totalCount=%d",
                    response.status_code,
                    total_count,
                )
                return True

            logger.warning("API 응답은 200이지만 totalCount=0 — 아직 불완전")
            return False

    except httpx.HTTPStatusError as e:
        logger.warning("API 헬스체크 실패 — HTTP %d", e.response.status_code)
        return False
    except httpx.RequestError as e:
        logger.warning("API 헬스체크 실패 — 요청 오류: %s", e)
        return False
    except Exception as e:
        logger.warning("API 헬스체크 실패 — 예상치 못한 오류: %s", e)
        return False


async def get_missing_count() -> int:
    """ingredients가 NULL인 약물 수를 조회한다.

    Returns:
        ingredients가 없는 약물 건수.
    """
    from sqlalchemy import text

    async with async_session_factory() as session:
        result = await session.execute(
            text("""
                SELECT COUNT(*)
                FROM drugs
                WHERE ingredients IS NULL
                   OR ingredients = '[]'::jsonb
                   OR ingredients = 'null'::jsonb
            """)
        )
        return result.scalar() or 0


async def run_collection(max_pages: int | None = None) -> dict[str, int]:
    """DrugPermissionCollector를 실행하여 성분 데이터를 수집한다.

    Args:
        max_pages: 최대 수집 페이지 수.

    Returns:
        수집 통계 딕셔너리.
    """
    collector = DrugPermissionCollector()
    try:
        async with async_session_factory() as session:
            stats = await collector.collect(session, max_pages=max_pages)
        return stats
    finally:
        await collector.close()


async def retry_loop(
    interval_min: int,
    max_retries: int,
    max_pages: int | None,
    once: bool,
) -> None:
    """API 복구를 감지하여 수집을 실행하는 메인 루프.

    Args:
        interval_min: 헬스체크 간격(분).
        max_retries: 최대 재시도 횟수 (0=무제한).
        max_pages: 수집 페이지 제한.
        once: True면 1회 시도 후 종료.
    """
    logger.info("=" * 60)
    logger.info("허가정보 API 자동 재시도 수집기 시작")
    logger.info("=" * 60)
    logger.info("시작 시각: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("헬스체크 간격: %d분", interval_min)
    logger.info("최대 재시도: %s", "무제한" if max_retries == 0 else f"{max_retries}회")
    if max_pages:
        logger.info("수집 페이지 제한: %d", max_pages)

    # DB 현황 조회
    missing = await get_missing_count()
    logger.info("현재 ingredients 누락 약물: %d건", missing)

    if missing == 0:
        logger.info("보강 대상 없음 — 종료")
        return

    attempt = 0

    while True:
        attempt += 1

        if max_retries > 0 and attempt > max_retries:
            logger.warning("최대 재시도 횟수(%d) 도달 — 종료", max_retries)
            return

        logger.info("-" * 40)
        logger.info("시도 #%d — 헬스체크 시작", attempt)

        healthy = await check_api_health()

        if not healthy:
            if once:
                logger.info("API 아직 다운 — --once 모드이므로 종료")
                return
            logger.info("API 아직 다운 — %d분 후 재시도", interval_min)
            await asyncio.sleep(interval_min * 60)
            continue

        # API 복구 감지 → 수집 시작
        logger.info("=" * 60)
        logger.info("API 복구 감지! 수집 시작")
        logger.info("=" * 60)

        start_time = time.time()
        try:
            stats = await run_collection(max_pages)
            elapsed = time.time() - start_time

            logger.info("수집 완료 — 소요 시간: %.1f초 (%.1f분)", elapsed, elapsed / 60)
            for key, value in stats.items():
                logger.info("  %-12s: %d", key, value)

            # 수집 후 현황 재확인
            remaining = await get_missing_count()
            logger.info("수집 후 ingredients 누락 약물: %d건", remaining)

            if remaining == 0 or stats.get("updated", 0) > 0:
                logger.info("수집 성공 — 종료")
                return

            # 업데이트 0건이고 누락이 남아있으면 재시도
            logger.warning(
                "업데이트 0건, 누락 %d건 — API 데이터 불완전, %d분 후 재시도",
                remaining,
                interval_min,
            )

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                "수집 중 오류 (%.1f초 경과): %s", elapsed, e, exc_info=True,
            )
            logger.info("%d분 후 재시도", interval_min)

        if once:
            logger.info("--once 모드이므로 종료")
            return

        await asyncio.sleep(interval_min * 60)


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="허가정보 API 자동 재시도 수집기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 1회 시도 (API 상태 확인용)
  python -m scripts.data-import.retry_permission_collector --once

  # 5분 간격 백그라운드 실행
  nohup python -m scripts.data-import.retry_permission_collector --interval 5 &

  # 로그 모니터링
  tail -f /tmp/permission_retry.log
        """,
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="헬스체크 간격 (분, 기본: 30)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="최대 재시도 횟수 (기본: 0=무제한)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="수집 페이지 제한 (테스트용)",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="/tmp/permission_retry.log",
        help="로그 파일 경로 (기본: /tmp/permission_retry.log)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="1회 시도 후 종료 (cron용)",
    )

    return parser.parse_args()


async def main() -> None:
    """메인 실행 함수."""
    args = parse_args()

    setup_logging(args.log_file)

    try:
        await retry_loop(
            interval_min=args.interval,
            max_retries=args.max_retries,
            max_pages=args.max_pages,
            once=args.once,
        )
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단 (Ctrl+C)")
    except Exception as e:
        logger.error("치명적 오류: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
