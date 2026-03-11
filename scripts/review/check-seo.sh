#!/usr/bin/env bash
# Review Agent — SEO 검사 스크립트
set -euo pipefail

WEB_DIR="${1:-src/web}"
ERRORS=0
WARNINGS=0

echo "=========================================="
echo "  SEO Check"
echo "=========================================="

# SEO-1: SSG 동적 라우트 페이지에 generateMetadata 확인
echo ""
echo "--- SEO-1: generateMetadata 확인 ---"
DYNAMIC_PAGES=$(find "$WEB_DIR/src/app" -name "page.tsx" -path "*\[*\]*" 2>/dev/null || true)
if [ -n "$DYNAMIC_PAGES" ]; then
    while IFS= read -r page_file; do
        if ! grep -q "generateMetadata\|export const metadata" "$page_file"; then
            echo "FAIL: $page_file — generateMetadata/metadata 없음"
            ERRORS=$((ERRORS + 1))
        fi
    done <<< "$DYNAMIC_PAGES"
    if [ $ERRORS -eq 0 ]; then
        echo "PASS: 모든 동적 페이지에 메타데이터 존재"
    fi
else
    echo "SKIP: 동적 라우트 페이지 없음"
fi

# SEO-4: robots.txt 존재 확인
echo ""
echo "--- SEO-4: robots.ts 존재 ---"
if [ -f "$WEB_DIR/src/app/robots.ts" ]; then
    echo "PASS"
else
    echo "FAIL: robots.ts 없음"
    ERRORS=$((ERRORS + 1))
fi

# SEO-5: sitemap.ts 존재 확인
echo ""
echo "--- SEO-5: sitemap.ts 존재 ---"
if [ -f "$WEB_DIR/src/app/sitemap.ts" ]; then
    echo "PASS"
else
    echo "FAIL: sitemap.ts 없음"
    ERRORS=$((ERRORS + 1))
fi

# SEO-6: JSON-LD 구조화 데이터 확인 (SSG 페이지)
echo ""
echo "--- SEO-6: JSON-LD 구조화 데이터 ---"
JSONLD_COUNT=$(grep -rl 'application/ld+json' "$WEB_DIR/src/app/" --include="*.tsx" 2>/dev/null | wc -l | xargs)
echo "INFO: JSON-LD 포함 페이지: ${JSONLD_COUNT}개"
if [ "$JSONLD_COUNT" -eq 0 ]; then
    echo "WARN: JSON-LD 구조화 데이터가 없음"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
