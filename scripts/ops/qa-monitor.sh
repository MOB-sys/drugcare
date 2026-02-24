#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — QA 모니터 (6시간 간격 cron 권장)
# 핵심 API 기능 E2E 스모크 테스트 실행
# ==============================================================================
set -euo pipefail

# --- 설정 ---
API_BASE="${API_BASE_URL:-http://localhost:8000}"
API_PREFIX="${API_BASE}/api/v1"
DEVICE_ID="qa-monitor-$(hostname)-$(date +%s)"
LOG_DIR="${LOG_DIR:-/var/log/yakmeogeo}"
LOG_FILE="${LOG_DIR}/qa-monitor.log"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"
TIMEOUT=15

PASSED=0
FAILED=0
TOTAL=0

mkdir -p "$LOG_DIR"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

log() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -sf -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"🧪 약먹어 QA 모니터 알림: ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# API 호출 함수
api_test() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_code="$4"
    local body="${5:-}"

    TOTAL=$((TOTAL + 1))

    local curl_args=(-sf -o /tmp/yakmeogeo-qa-response.json -w "%{http_code}" \
        --max-time "$TIMEOUT" \
        -H "X-Device-ID: $DEVICE_ID" \
        -H "Content-Type: application/json")

    if [ -n "$body" ]; then
        curl_args+=(-X "$method" -d "$body")
    else
        curl_args+=(-X "$method")
    fi

    local http_code
    http_code=$(curl "${curl_args[@]}" "${API_PREFIX}${endpoint}" 2>/dev/null || echo "000")

    if [ "$http_code" = "$expected_code" ]; then
        log "  ✅ PASS: ${name} (HTTP ${http_code})"
        PASSED=$((PASSED + 1))
    else
        log "  ❌ FAIL: ${name} — 예상: ${expected_code}, 실제: ${http_code}"
        FAILED=$((FAILED + 1))
    fi
}

# --- QA 테스트 실행 ---
log "========================================"
log "=== QA 모니터 스모크 테스트 시작 ==="
log "========================================"

# 1. 헬스체크
log "--- [1/6] 헬스체크 ---"
api_test "헬스체크 응답" "GET" "/health" "200"

# 2. 약물 검색
log "--- [2/6] 약물 검색 API ---"
api_test "약물 검색 (타이레놀)" "GET" "/drugs/search?query=%ED%83%80%EC%9D%B4%EB%A0%88%EB%86%80&limit=5" "200"
api_test "약물 검색 (빈 쿼리)" "GET" "/drugs/search?query=&limit=5" "200"

# 3. 영양제 검색
log "--- [3/6] 영양제 검색 API ---"
api_test "영양제 검색 (비타민)" "GET" "/supplements/search?query=%EB%B9%84%ED%83%80%EB%AF%BC&limit=5" "200"

# 4. 상호작용 체크
log "--- [4/6] 상호작용 체크 API ---"
api_test "상호작용 체크 (빈 목록)" "POST" "/interactions/check" "422" '{"items": []}'

# 5. 복약함 API
log "--- [5/6] 복약함 API ---"
api_test "복약함 조회" "GET" "/cabinet" "200"

# 6. 리마인더 API
log "--- [6/6] 리마인더 API ---"
api_test "리마인더 목록 조회" "GET" "/reminders" "200"

# --- 결과 집계 ---
log "========================================"
log "=== QA 모니터 결과 ==="
log "  전체: ${TOTAL} | 성공: ${PASSED} | 실패: ${FAILED}"
log "========================================"

if [ "$FAILED" -gt 0 ]; then
    send_alert "스모크 테스트 실패 ${FAILED}/${TOTAL}건"
    exit 1
else
    log "모든 스모크 테스트 통과"
    exit 0
fi
