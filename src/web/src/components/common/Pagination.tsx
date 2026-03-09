/** 페이지네이션 컴포넌트 — SEO 친화적 Link 기반. */

import Link from "next/link";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  /** 페이지 번호가 삽입될 href 패턴. "{page}"를 페이지 번호로 치환한다. */
  basePath: string;
}

/** 페이지 번호 배열 생성 (말줄임 포함). */
function getPageNumbers(current: number, total: number): (number | "...")[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | "...")[] = [1];

  if (current > 3) pages.push("...");

  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (current < total - 2) pages.push("...");

  pages.push(total);
  return pages;
}

/** href를 생성한다. basePath의 "{page}"를 페이지 번호로 치환. */
function buildHref(basePath: string, page: number): string {
  return basePath.replace("{page}", String(page));
}

export function Pagination({ currentPage, totalPages, basePath }: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages = getPageNumbers(currentPage, totalPages);

  return (
    <nav className="flex items-center justify-center gap-1 mt-8" aria-label="페이지 탐색">
      {/* 이전 페이지 */}
      {currentPage > 1 ? (
        <Link
          href={buildHref(basePath, currentPage - 1)}
          className="px-3 py-2 rounded-lg text-sm font-medium text-[var(--color-primary)] hover:bg-[var(--color-primary-50)] transition-colors"
          aria-label="이전 페이지"
        >
          &laquo; 이전
        </Link>
      ) : (
        <span className="px-3 py-2 rounded-lg text-sm font-medium text-gray-300 cursor-default">
          &laquo; 이전
        </span>
      )}

      {/* 페이지 번호 */}
      {pages.map((p, idx) =>
        p === "..." ? (
          <span
            key={`ellipsis-${idx}`}
            className="w-10 h-10 flex items-center justify-center text-sm text-gray-400"
          >
            ...
          </span>
        ) : p === currentPage ? (
          <span
            key={p}
            className="w-10 h-10 flex items-center justify-center rounded-lg text-sm font-bold bg-[var(--color-primary)] text-white"
            aria-current="page"
          >
            {p}
          </span>
        ) : (
          <Link
            key={p}
            href={buildHref(basePath, p)}
            className="w-10 h-10 flex items-center justify-center rounded-lg text-sm font-medium text-gray-700 hover:bg-[var(--color-primary-50)] transition-colors"
          >
            {p}
          </Link>
        ),
      )}

      {/* 다음 페이지 */}
      {currentPage < totalPages ? (
        <Link
          href={buildHref(basePath, currentPage + 1)}
          className="px-3 py-2 rounded-lg text-sm font-medium text-[var(--color-primary)] hover:bg-[var(--color-primary-50)] transition-colors"
          aria-label="다음 페이지"
        >
          다음 &raquo;
        </Link>
      ) : (
        <span className="px-3 py-2 rounded-lg text-sm font-medium text-gray-300 cursor-default">
          다음 &raquo;
        </span>
      )}
    </nav>
  );
}
