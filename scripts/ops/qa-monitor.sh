#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — QA 스모크 테스트 (6시간 간격 cron 권장)
# 듀얼 플랫폼: API + 웹 페이지 + SEO 인덱싱 통합 검증
# ==============================================================================
set -euo pipefail

# --- 설정 ---
PROJECT_DIR="${PROJECT_DIR:-$HOME/workspace/yakmeogeo}"
API_BASE="${API_BASE_URL:-http://localhost:8000}"
WEB_BASE="${WEB_BASE_URL:-http://localhost:3000}"
API_PREFIX="${API_BASE}/api/v1"
DEVICE_ID="qa-monitor-$(hostname)-$(date +%s)"
TIMESTAMP=$(date +%Y%m%d-%H%M)
REPORT_DIR="${PROJECT_DIR}/.agents/ops-squad/qa-monitor/reports"
REPORT_FILE="${REPORT_DIR}/QA-${TIMESTAMP}.md"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"
TIMEOUT=15

PASS=0
FAIL=0
RESULTS=""

mkdir -p "$REPORT_DIR"

check() {
    local name="$1" url="$2" method="${3:-GET}" body="$4"

    local curl_args=(-s -o /dev/null -w '%{http_code}' --max-time "$TIMEOUT"
        -H "X-Device-ID: $DEVICE_ID"
        -H "Content-Type: application/json")

    if [ "$method" = "POST" ] && [ -n "$body" ]; then
        STATUS=$(curl "${curl_args[@]}" -X POST -d "$body" "$url" 2>/dev/null || echo "000")
    else
        STATUS=$(curl "${curl_args[@]}" "$url" 2>/dev/null || echo "000")
    fi

    if [ "$STATUS" = "200" ] || [ "$STATUS" = "201" ]; then
        RESULTS="${RESULTS}\n| ${name} | ✅ ${STATUS} | PASS |"
        PASS=$((PASS + 1))
    else
        RESULTS="${RESULTS}\n| ${name} | ❌ ${STATUS} | FAIL |"
        FAIL=$((FAIL + 1))
    fi
}

# --- API 테스트 ---
check "API Health" "${API_PREFIX}/health" "GET" ""
check "Drug Search" "${API_PREFIX}/drugs/search?query=%ED%83%80%EC%9D%B4%EB%A0%88%EB%86%80&limit=5" "GET" ""
check "Supplement Search" "${API_PREFIX}/supplements/search?query=%EB%B9%84%ED%83%80%EB%AF%BCD&limit=5" "GET" ""
check "Drug Slugs" "${API_PREFIX}/drugs/slugs" "GET" ""
check "Drug Count" "${API_PREFIX}/drugs/count" "GET" ""
check "Interaction Check" "${API_PREFIX}/interactions/check" "POST" \
    '{"items":[{"item_type":"drug","item_id":"1"},{"item_type":"drug","item_id":"2"}]}'

# --- 웹 테스트 ---
check "Web Home" "${WEB_BASE}/" "GET" ""
check "Web Check" "${WEB_BASE}/check" "GET" ""
check "Sitemap" "${WEB_BASE}/sitemap.xml" "GET" ""
check "Robots.txt" "${WEB_BASE}/robots.txt" "GET" ""

TOTAL=$((PASS + FAIL))

# --- 보고서 생성 ---
cat > "$REPORT_FILE" << EOF
# QA 스모크 테스트 보고서
- **시간:** $(date '+%Y-%m-%d %H:%M')
- **결과:** ${PASS}/${TOTAL} 통과 $([ "$FAIL" -gt 0 ] && echo "⚠️" || echo "✅")

## 상세 결과
| 테스트 | 상태 | 판정 |
|--------|------|------|
$(echo -e "$RESULTS")

## 조치 필요
$([ "$FAIL" -gt 0 ] && echo "❌ ${FAIL}개 테스트 실패 — 확인 필요" || echo "없음")
EOF

# --- 알림 ---
if [ "$FAIL" -gt 0 ] && [ -n "$ALERT_WEBHOOK" ]; then
    curl -sf -X POST "$ALERT_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"🧪 약먹어 QA: ${FAIL}/${TOTAL} 테스트 실패\"}" \
        > /dev/null 2>&1 || true
fi

echo "✅ QA 테스트 완료: ${PASS}/${TOTAL} 통과 — ${REPORT_FILE}"
