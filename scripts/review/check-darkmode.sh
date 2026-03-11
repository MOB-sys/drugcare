#!/usr/bin/env bash
# Review Agent — 다크모드 일관성 검사 스크립트
set -euo pipefail

WEB_DIR="${1:-src/web}"
WARNINGS=0

echo "=========================================="
echo "  Dark Mode Check"
echo "=========================================="

# DM-1: 하드코딩 색상 + dark: 프리픽스 누락 감지
# CSS 변수(bg-surface, text-text 등) 사용 시에는 자동 전환되므로 제외
# 직접 색상값(bg-white, bg-gray-100 등) 사용 시 dark: 대응 필요
echo ""
echo "--- DM-1: dark: 프리픽스 없는 하드코딩 색상 ---"

# 검사 대상: bg-white, bg-gray-*, text-gray-*, border-gray-* 등 (dark: 없이 사용)
HARDCODED=$(grep -rn \
    -e 'bg-white' -e 'bg-black' \
    -e 'bg-gray-' -e 'bg-slate-' -e 'bg-zinc-' -e 'bg-neutral-' \
    -e 'text-gray-' -e 'text-slate-' \
    -e 'border-gray-' -e 'border-slate-' \
    "$WEB_DIR/src/" --include="*.tsx" \
    | grep -v '\.test\.' \
    | grep -v 'dark:' \
    | grep -v '// review-ok' \
    | grep -v 'node_modules' \
    || true)

if [ -n "$HARDCODED" ]; then
    COUNT=$(echo "$HARDCODED" | wc -l | xargs)
    echo "WARN: dark: 프리픽스 없는 하드코딩 색상 ${COUNT}건:"
    echo "$HARDCODED" | head -30
    if [ "$COUNT" -gt 30 ]; then
        echo "... 외 $((COUNT - 30))건 생략"
    fi
    WARNINGS=$((WARNINGS + 1))
else
    echo "PASS"
fi

# DM-2: CSS 변수 사용 권장 (bg-surface, text-text 등)
echo ""
echo "--- DM-2: CSS 변수 사용 현황 ---"
CSS_VAR_COUNT=$(grep -rc 'bg-surface\|bg-card\|text-text\|text-muted\|border-border' \
    "$WEB_DIR/src/" --include="*.tsx" 2>/dev/null | awk -F: '{s+=$2} END {print s}')
echo "INFO: CSS 변수 사용 횟수: ${CSS_VAR_COUNT:-0}회"

echo ""
echo "=========================================="
echo "  결과: 경고 ${WARNINGS}건"
echo "=========================================="
# 다크모드는 경고만 (실패로 블록하지 않음)
exit 0
