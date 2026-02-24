#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Ops — 헬스체크 스크립트 (30분 간격 cron 권장)
# ==============================================================================
set -euo pipefail

# --- 설정 ---
API_BASE="${API_BASE_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="${API_BASE}/api/v1/health"
LOG_DIR="${LOG_DIR:-/var/log/yakmeogeo}"
LOG_FILE="${LOG_DIR}/health-check.log"
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"  # Slack/Discord webhook (선택)
TIMEOUT=10

# 로그 디렉토리 생성
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
            -d "{\"text\": \"🚨 약먹어 헬스체크 알림: ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# --- 헬스체크 실행 ---
log "=== 헬스체크 시작 ==="

# API 헬스 엔드포인트 호출
HTTP_CODE=$(curl -sf -o /tmp/yakmeogeo-health.json -w "%{http_code}" \
    --max-time "$TIMEOUT" "$HEALTH_ENDPOINT" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    # 응답 파싱
    STATUS=$(python3 -c "
import json, sys
try:
    data = json.load(open('/tmp/yakmeogeo-health.json'))
    health = data.get('data', {})
    print(f\"status={health.get('status', 'unknown')} db={health.get('database', 'unknown')} redis={health.get('redis', 'unknown')}\")
except Exception as e:
    print(f'parse_error={e}')
" 2>/dev/null || echo "parse_error")

    if echo "$STATUS" | grep -q "status=healthy"; then
        log "✅ 정상 — $STATUS"
    else
        log "⚠️  경고 — 서비스 저하: $STATUS"
        send_alert "서비스 저하 감지: $STATUS"
    fi
else
    log "🔴 실패 — API 응답 없음 (HTTP $HTTP_CODE)"
    send_alert "API 서버 응답 없음 (HTTP $HTTP_CODE)"
fi

# Docker 컨테이너 상태 확인 (Docker가 설치된 경우)
if command -v docker &> /dev/null; then
    log "--- Docker 컨테이너 상태 ---"
    for container in yakmeogeo-backend yakmeogeo-db yakmeogeo-redis; do
        STATE=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        if [ "$STATE" = "running" ]; then
            log "  ✅ $container: $STATE"
        else
            log "  🔴 $container: $STATE"
            send_alert "컨테이너 이상: $container ($STATE)"
        fi
    done
fi

# 디스크 사용률 확인
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 85 ]; then
    log "⚠️  디스크 사용률 높음: ${DISK_USAGE}%"
    send_alert "디스크 사용률 ${DISK_USAGE}% (임계값 85%)"
else
    log "  💾 디스크 사용률: ${DISK_USAGE}%"
fi

log "=== 헬스체크 완료 ==="
