#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — 헬스체크 스크립트 (30분 간격 cron 권장)
# 듀얼 플랫폼: API + 웹 + 인프라 통합 감시
# ==============================================================================
set -euo pipefail

# --- 설정 ---
PROJECT_DIR="${PROJECT_DIR:-$HOME/workspace/yakmeogeo}"
API_BASE="${API_BASE_URL:-http://localhost:8000}"
WEB_BASE="${WEB_BASE_URL:-http://localhost:3000}"
HEALTH_ENDPOINT="${API_BASE}/api/v1/health"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/.agents/ops-squad/health-checker/logs}"
TIMESTAMP=$(date +%Y%m%d-%H%M)
LOG_FILE="${LOG_DIR}/HEALTH-${TIMESTAMP}.json"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"
TIMEOUT=10

mkdir -p "$LOG_DIR"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

send_alert() {
    local message="$1"
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -sf -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"🚨 약먹어 헬스체크 알림: ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# --- API 헬스체크 ---
API_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$HEALTH_ENDPOINT" --max-time "$TIMEOUT" 2>/dev/null || echo "000")
API_TIME=$(curl -s -o /dev/null -w '%{time_total}' "$HEALTH_ENDPOINT" --max-time "$TIMEOUT" 2>/dev/null || echo "0")

# --- 웹 헬스체크 ---
WEB_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$WEB_BASE" --max-time "$TIMEOUT" 2>/dev/null || echo "000")
WEB_TIME=$(curl -s -o /dev/null -w '%{time_total}' "$WEB_BASE" --max-time "$TIMEOUT" 2>/dev/null || echo "0")

# --- sitemap 확인 ---
SITEMAP_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$WEB_BASE/sitemap.xml" --max-time "$TIMEOUT" 2>/dev/null || echo "000")

# --- Docker 상태 ---
DOCKER_STATUS="N/A"
if command -v docker &> /dev/null; then
    DOCKER_STATUS=$(docker ps --format '{{.Names}}: {{.Status}}' 2>/dev/null | tr '\n' ', ' || echo "docker not running")
fi

# --- SSL 만료일 ---
SSL_EXPIRY="N/A"
DOMAIN="${DOMAIN:-pillright.com}"
if [ "$WEB_STATUS" != "000" ] && echo "$WEB_BASE" | grep -q "https"; then
    SSL_EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "unknown")
fi

# --- 디스크 사용량 ---
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')

# --- 종합 판정 ---
if [ "$API_STATUS" = "200" ] && [ "$WEB_STATUS" = "200" ]; then
    OVERALL="ok"
elif [ "$API_STATUS" = "000" ] || [ "$WEB_STATUS" = "000" ]; then
    OVERALL="down"
else
    OVERALL="degraded"
fi

# --- JSON 저장 ---
cat > "$LOG_FILE" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "overall": "$OVERALL",
  "api": { "status": $API_STATUS, "response_time": $API_TIME },
  "web": { "status": $WEB_STATUS, "response_time": $WEB_TIME },
  "sitemap": { "status": $SITEMAP_STATUS },
  "docker": "$DOCKER_STATUS",
  "ssl_expiry": "$SSL_EXPIRY",
  "disk_usage_pct": $DISK_USAGE
}
EOF

# --- 알림 ---
if [ "$OVERALL" != "ok" ]; then
    echo "🔴 약먹어 서비스 이상 감지: API=$API_STATUS, WEB=$WEB_STATUS"
    send_alert "서비스 이상: API=$API_STATUS WEB=$WEB_STATUS"
fi

if [ "$DISK_USAGE" -gt 90 ]; then
    echo "⚠️  디스크 사용률 높음: ${DISK_USAGE}%"
    send_alert "디스크 사용률 ${DISK_USAGE}%"
fi

echo "✅ 헬스체크 완료 [$OVERALL]: $LOG_FILE"
