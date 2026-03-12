#!/usr/bin/env bash
# ============================================================================
# Review Agent — 번들 크기 모니터
# Next.js 빌드 결과물 크기를 추적하고 임계값 초과 시 경고
#
# 사용법:
#   ./check-bundle-size.sh [web_dir]
#   ./check-bundle-size.sh src/web --update    # 기준선 갱신
# ============================================================================
set -euo pipefail

WEB_DIR="${1:-src/web}"
MODE="check"
[[ "${2:-}" == "--update" ]] && MODE="update"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASELINE_FILE="${SCRIPT_DIR}/snapshots/bundle-baseline.json"
ERRORS=0
WARNINGS=0

# 임계값 (KB)
TOTAL_JS_MAX=600          # 전체 JS 번들 합계
SINGLE_CHUNK_MAX=150      # 개별 청크 최대
TOTAL_CSS_MAX=100         # 전체 CSS 합계
FIRST_LOAD_MAX=200        # First Load JS 최대

echo "=========================================="
echo "  Bundle Size Check"
echo "=========================================="

# .next 빌드 결과 확인
NEXT_DIR="${WEB_DIR}/.next"
if [ ! -d "$NEXT_DIR" ]; then
    echo ""
    echo "SKIP: .next 디렉토리 없음"
    echo "  'npm run build' 실행 후 재시도하세요."
    exit 0
fi

# --- B-1: 전체 JS 번들 크기 ---
echo ""
echo "--- B-1: JavaScript 번들 크기 ---"

CHUNKS_DIR="${NEXT_DIR}/static/chunks"
if [ -d "$CHUNKS_DIR" ]; then
    TOTAL_JS_KB=$(find "$CHUNKS_DIR" -name "*.js" -exec du -k {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
    echo "  전체 JS: ${TOTAL_JS_KB}KB (임계값 ${TOTAL_JS_MAX}KB)"

    if [ "$TOTAL_JS_KB" -gt "$TOTAL_JS_MAX" ]; then
        echo "  WARN: JS 번들 크기 초과"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  PASS"
    fi

    # 가장 큰 청크 Top 5
    echo ""
    echo "  Top 5 청크:"
    find "$CHUNKS_DIR" -name "*.js" -exec du -k {} + 2>/dev/null \
        | sort -rn | head -5 | while read -r size name; do
        label=""
        if [ "$size" -gt "$SINGLE_CHUNK_MAX" ]; then
            label=" ⚠️ 초과"
            WARNINGS=$((WARNINGS + 1))
        fi
        echo "    ${size}KB  $(basename "$name")${label}"
    done
else
    echo "  SKIP: chunks 디렉토리 없음"
fi

# --- B-2: CSS 번들 크기 ---
echo ""
echo "--- B-2: CSS 번들 크기 ---"

CSS_DIR="${NEXT_DIR}/static/css"
if [ -d "$CSS_DIR" ]; then
    TOTAL_CSS_KB=$(find "$CSS_DIR" -name "*.css" -exec du -k {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
    echo "  전체 CSS: ${TOTAL_CSS_KB}KB (임계값 ${TOTAL_CSS_MAX}KB)"

    if [ "$TOTAL_CSS_KB" -gt "$TOTAL_CSS_MAX" ]; then
        echo "  WARN: CSS 번들 크기 초과"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  PASS"
    fi
else
    echo "  SKIP: css 디렉토리 없음"
    TOTAL_CSS_KB=0
fi

# --- B-3: 빌드 로그에서 라우트별 크기 ---
echo ""
echo "--- B-3: 빌드 출력 .next 총 크기 ---"

NEXT_TOTAL_KB=$(du -sk "$NEXT_DIR" 2>/dev/null | awk '{print $1}')
NEXT_TOTAL_MB=$(echo "scale=1; $NEXT_TOTAL_KB / 1024" | bc 2>/dev/null || echo "?")
echo "  .next 총 크기: ${NEXT_TOTAL_MB}MB"

# --- B-4: 이전 기준선 대비 ---
echo ""
echo "--- B-4: 이전 기준선 대비 ---"

CURRENT_DATA="{\"total_js_kb\": ${TOTAL_JS_KB:-0}, \"total_css_kb\": ${TOTAL_CSS_KB:-0}, \"next_total_kb\": ${NEXT_TOTAL_KB:-0}, \"date\": \"$(date '+%Y-%m-%d')\"}"

if [ "$MODE" = "update" ]; then
    mkdir -p "$(dirname "$BASELINE_FILE")"
    echo "$CURRENT_DATA" > "$BASELINE_FILE"
    echo "  기준선 갱신: ${BASELINE_FILE}"
elif [ -f "$BASELINE_FILE" ]; then
    PREV_JS=$(python3 -c "import json; print(json.load(open('$BASELINE_FILE')).get('total_js_kb', 0))" 2>/dev/null || echo "0")
    PREV_CSS=$(python3 -c "import json; print(json.load(open('$BASELINE_FILE')).get('total_css_kb', 0))" 2>/dev/null || echo "0")
    PREV_DATE=$(python3 -c "import json; print(json.load(open('$BASELINE_FILE')).get('date', '?'))" 2>/dev/null || echo "?")

    JS_DIFF=$((${TOTAL_JS_KB:-0} - PREV_JS))
    CSS_DIFF=$((${TOTAL_CSS_KB:-0} - PREV_CSS))

    echo "  기준선 (${PREV_DATE}):"
    if [ "$JS_DIFF" -gt 50 ]; then
        echo "    JS: ${PREV_JS}KB → ${TOTAL_JS_KB:-0}KB (+${JS_DIFF}KB) ⚠️ 급증"
        WARNINGS=$((WARNINGS + 1))
    elif [ "$JS_DIFF" -gt 0 ]; then
        echo "    JS: ${PREV_JS}KB → ${TOTAL_JS_KB:-0}KB (+${JS_DIFF}KB)"
    elif [ "$JS_DIFF" -lt 0 ]; then
        echo "    JS: ${PREV_JS}KB → ${TOTAL_JS_KB:-0}KB (${JS_DIFF}KB) 감소"
    else
        echo "    JS: ${TOTAL_JS_KB:-0}KB (변동 없음)"
    fi

    if [ "$CSS_DIFF" -gt 20 ]; then
        echo "    CSS: ${PREV_CSS}KB → ${TOTAL_CSS_KB:-0}KB (+${CSS_DIFF}KB) ⚠️ 급증"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "    CSS: ${PREV_CSS}KB → ${TOTAL_CSS_KB:-0}KB (${CSS_DIFF:+${CSS_DIFF}}KB)"
    fi
else
    echo "  INFO: 기준선 없음 (--update로 생성)"
fi

# --- 결과 ---
echo ""
echo "=========================================="
echo "  결과: 오류 ${ERRORS}건, 경고 ${WARNINGS}건"
echo "=========================================="
exit $ERRORS
