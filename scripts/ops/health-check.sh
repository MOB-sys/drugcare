#!/usr/bin/env bash
# ==============================================================================
# 약잘알 Ops — 헬스체크 + 자동 복구 스크립트
# 크론: */5 * * * * /opt/drugcare/scripts/ops/health-check.sh >> /var/log/yakmeogeo-health.log 2>&1
# ==============================================================================

# --- 설정 ---
API_BASE="${API_BASE_URL:-https://api.pillright.com}"
WEB_BASE="${WEB_BASE_URL:-https://pillright.com}"
HEALTH_ENDPOINT="${API_BASE}/api/v1/health"
LOG_DIR="${LOG_DIR:-/var/log}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
ALERT_WEBHOOK="${ALERT_WEBHOOK_URL:-}"
BACKEND_CONTAINER="yakmeogeo-backend"
REDIS_CONTAINER="yakmeogeo-redis"
DOMAIN="pillright.com"
TIMEOUT=10

log() {
    echo "[$TIMESTAMP] $1"
}

ESCALATION_SCRIPT="${ESCALATION_SCRIPT:-$(dirname "$0")/../maintenance/escalation/alert-escalation.sh}"

send_alert() {
    local alert_key="$1"
    local message="$2"
    local severity="${3:-WARNING}"

    # 에스컬레이션 시스템이 있으면 위임 (심각도별 차등 재알림 + SMS/전화)
    if [ -x "$ESCALATION_SCRIPT" ]; then
        "$ESCALATION_SCRIPT" "$alert_key" "$severity" "$message"
        return
    fi

    # 폴백: 기존 단순 알림 (에스컬레이션 미설치 시)
    local stamp_file="/tmp/yakmeogeo-alert-${alert_key}"
    if [ -f "$stamp_file" ]; then
        local last=$(cat "$stamp_file")
        local now=$(date +%s)
        if [ $((now - last)) -lt 3600 ]; then
            return
        fi
    fi
    date +%s > "$stamp_file"
    log "ALERT: $message"
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -sf -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"[약잘알] ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# --- 1. 백엔드 API 헬스체크 + 자동 복구 ---
API_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$HEALTH_ENDPOINT" --max-time "$TIMEOUT" 2>/dev/null || echo "000")
API_TIME=$(curl -s -o /dev/null -w '%{time_total}' "$HEALTH_ENDPOINT" --max-time "$TIMEOUT" 2>/dev/null || echo "0")

if [ "$API_STATUS" = "200" ]; then
    log "OK: Backend API (HTTP $API_STATUS, ${API_TIME}s)"
else
    log "FAIL: Backend API (HTTP $API_STATUS)"
    log "ACTION: Restarting $BACKEND_CONTAINER..."
    docker restart "$BACKEND_CONTAINER" 2>/dev/null || true
    sleep 30
    API_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$HEALTH_ENDPOINT" --max-time "$TIMEOUT" 2>/dev/null || echo "000")
    if [ "$API_STATUS" = "200" ]; then
        log "RECOVERED: Backend auto-recovered"
        send_alert "backend" "Backend was down, auto-recovered after restart" "INFO"
    else
        log "CRITICAL: Backend still down after restart"
        send_alert "backend_down" "Backend is DOWN! Auto-restart failed (HTTP $API_STATUS)" "CRITICAL"
    fi
fi

# --- 2. Redis 헬스체크 + 자동 복구 ---
REDIS_STATUS=$(docker inspect --format='{{.State.Status}}' "$REDIS_CONTAINER" 2>/dev/null || echo "unknown")
if [ "$REDIS_STATUS" = "running" ]; then
    log "OK: Redis running"
else
    log "FAIL: Redis status=$REDIS_STATUS"
    docker restart "$REDIS_CONTAINER" 2>/dev/null || true
    sleep 10
    send_alert "redis_down" "Redis was down ($REDIS_STATUS), restarted" "CRITICAL"
fi

# --- 3. 웹(Vercel) 헬스체크 ---
WEB_STATUS=$(curl -s -o /dev/null -w '%{http_code}' "$WEB_BASE" --max-time "$TIMEOUT" 2>/dev/null || echo "000")
WEB_TIME=$(curl -s -o /dev/null -w '%{time_total}' "$WEB_BASE" --max-time "$TIMEOUT" 2>/dev/null || echo "0")
if [ "$WEB_STATUS" = "200" ]; then
    log "OK: Web (HTTP $WEB_STATUS, ${WEB_TIME}s)"
else
    log "WARN: Web unreachable (HTTP $WEB_STATUS)"
    send_alert "web_down" "Web (pillright.com) unreachable: HTTP $WEB_STATUS" "WARNING"
fi

# --- 4. 디스크 체크 + 자동 정리 ---
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    log "OK: Disk ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -lt 95 ]; then
    log "WARN: Disk ${DISK_USAGE}%"
    docker image prune -f > /dev/null 2>&1 || true
    docker container prune -f > /dev/null 2>&1 || true
    send_alert "disk_warning" "Disk usage ${DISK_USAGE}%, auto-pruned Docker" "WARNING"
else
    log "CRITICAL: Disk ${DISK_USAGE}%!"
    send_alert "disk_critical" "Disk CRITICAL: ${DISK_USAGE}%!" "CRITICAL"
fi

# --- 5. 메모리 체크 ---
MEM_AVAIL=$(free -m 2>/dev/null | awk '/^Mem:/ {print $7}' || echo "0")
if [ "$MEM_AVAIL" -gt 200 ]; then
    log "OK: Memory ${MEM_AVAIL}MB available"
elif [ "$MEM_AVAIL" -gt 100 ]; then
    log "WARN: Memory low ${MEM_AVAIL}MB"
    send_alert "high_memory" "Available memory low: ${MEM_AVAIL}MB" "WARNING"
else
    log "CRITICAL: Memory ${MEM_AVAIL}MB!"
    send_alert "high_memory" "Memory CRITICAL: ${MEM_AVAIL}MB!" "CRITICAL"
fi

# --- 6. SSL 만료 체크 (매일 09시에만) ---
HOUR=$(date +%H)
if [ "$HOUR" = "09" ]; then
    SSL_EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || echo "")
    if [ -n "$SSL_EXPIRY" ]; then
        EXPIRY_EPOCH=$(date -d "$SSL_EXPIRY" +%s 2>/dev/null || echo "0")
        NOW_EPOCH=$(date +%s)
        if [ "$EXPIRY_EPOCH" -gt 0 ]; then
            DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
            if [ "$DAYS_LEFT" -gt 14 ]; then
                log "OK: SSL expires in ${DAYS_LEFT} days"
            else
                log "WARN: SSL expires in ${DAYS_LEFT} days!"
                send_alert "ssl_expiry" "SSL expires in ${DAYS_LEFT} days! Renew ASAP" "WARNING"
            fi
        fi
    fi
fi

# --- 종합 ---
if [ "$API_STATUS" = "200" ] && [ "$WEB_STATUS" = "200" ]; then
    OVERALL="ok"
elif [ "$API_STATUS" = "000" ] || [ "$WEB_STATUS" = "000" ]; then
    OVERALL="down"
else
    OVERALL="degraded"
fi
log "=== Result: $OVERALL ==="
