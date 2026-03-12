#!/bin/bash
# ============================================================================
# 알림 에스컬레이션 시스템
# 심각도별 차등 재알림 + Claude 미응답 시 SMS/전화 에스컬레이션
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../config/.env.mt" 2>/dev/null || true
[ -f "${SCRIPT_DIR}/../config/.env.mt.local" ] && source "${SCRIPT_DIR}/../config/.env.mt.local"

STATE_DIR="${STATE_DIR:-$HOME/.pillright-mt/state}/escalation"
LOG_FILE="${LOG_DIR:-$HOME/.pillright-mt/logs}/escalation.log"

# 에스컬레이션 타이밍 (초)
ESCALATION_INTERVALS_INFO=3600
ESCALATION_INTERVALS_WARNING=1800
ESCALATION_INTERVALS_CRITICAL=600
ESCALATION_INTERVALS_DOWN=300
SMS_ESCALATION_AFTER=1800
PHONE_ESCALATION_AFTER=3600

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ESCALATION] $1" | tee -a "$LOG_FILE"
}

get_interval() {
    case "$1" in
        INFO)     echo "$ESCALATION_INTERVALS_INFO" ;;
        WARNING)  echo "$ESCALATION_INTERVALS_WARNING" ;;
        CRITICAL) echo "$ESCALATION_INTERVALS_CRITICAL" ;;
        DOWN)     echo "$ESCALATION_INTERVALS_DOWN" ;;
        *)        echo "$ESCALATION_INTERVALS_WARNING" ;;
    esac
}

# 상태 파일: first_seen / last_notified / level / count
read_state() {
    local f="$1"
    if [[ -f "$f" ]]; then
        FIRST_SEEN=$(sed -n '1p' "$f"); LAST_NOTIFIED=$(sed -n '2p' "$f")
        ESCALATION_LEVEL=$(sed -n '3p' "$f"); NOTIFY_COUNT=$(sed -n '4p' "$f")
    else
        FIRST_SEEN=""; LAST_NOTIFIED=""; ESCALATION_LEVEL=0; NOTIFY_COUNT=0
    fi
}

write_state() {
    mkdir -p "$(dirname "$1")"
    printf '%s\n%s\n%s\n%s\n' "$2" "$3" "$4" "$5" > "$1"
}

send_webhook() {
    if [[ -n "${ALERT_WEBHOOK_URL:-}" ]]; then
        curl -s -X POST "$ALERT_WEBHOOK_URL" -H "Content-Type: application/json" \
            -d "{\"text\": \"$1\"}" > /dev/null 2>&1 || true
    fi
}

send_sms() {
    if [[ -n "${SMS_WEBHOOK_URL:-}" && -n "${OWNER_PHONE:-}" ]]; then
        curl -s -X POST "$SMS_WEBHOOK_URL" -H "Content-Type: application/json" \
            -d "{\"to\": \"${OWNER_PHONE}\", \"message\": \"$1\"}" > /dev/null 2>&1 || true
        log "SMS sent to ${OWNER_PHONE}"
    fi
}

send_phone() {
    if [[ -n "${PHONE_WEBHOOK_URL:-}" && -n "${OWNER_PHONE:-}" ]]; then
        curl -s -X POST "$PHONE_WEBHOOK_URL" -H "Content-Type: application/json" \
            -d "{\"to\": \"${OWNER_PHONE}\", \"message\": \"$1\"}" > /dev/null 2>&1 || true
        log "Phone call triggered to ${OWNER_PHONE}"
    fi
}

process_alert() {
    local alert_key="$1" severity="$2" message="$3"
    local now; now=$(date +%s)
    local state_file="${STATE_DIR}/${alert_key}.state"

    read_state "$state_file"

    # 신규
    if [[ -z "$FIRST_SEEN" ]]; then
        write_state "$state_file" "$now" "$now" "0" "1"
        send_webhook "🔔 [${severity}] ${message} (신규 감지)"
        log "New: ${alert_key} [${severity}]"
        return
    fi

    # 재알림 간격 체크
    local interval; interval=$(get_interval "$severity")
    [[ $((now - LAST_NOTIFIED)) -lt $interval ]] && return

    local duration=$((now - FIRST_SEEN))
    local duration_min=$((duration / 60))
    NOTIFY_COUNT=$((NOTIFY_COUNT + 1))

    # 에스컬레이션 레벨 결정
    local new_level=$ESCALATION_LEVEL
    [[ $duration -ge $PHONE_ESCALATION_AFTER && $ESCALATION_LEVEL -lt 2 ]] && new_level=2
    [[ $duration -ge $SMS_ESCALATION_AFTER && $ESCALATION_LEVEL -lt 1 && $new_level -lt 1 ]] && new_level=1

    case $new_level in
        0) send_webhook "🔁 [${severity}] ${message} (지속 ${duration_min}분, ${NOTIFY_COUNT}회차)" ;;
        1)
            [[ $new_level -gt $ESCALATION_LEVEL ]] && \
                send_webhook "⬆️ [${severity}] SMS 에스컬레이션: ${message} (지속 ${duration_min}분)"
            send_sms "[PillRight ${severity}] ${message} - ${duration_min}분 지속"
            ;;
        2)
            [[ $new_level -gt $ESCALATION_LEVEL ]] && \
                send_webhook "🚨 [${severity}] 전화 에스컬레이션: ${message} (지속 ${duration_min}분)"
            send_phone "PillRight 서비스 장애. ${severity}. ${message}. ${duration_min}분 지속중."
            ;;
    esac

    write_state "$state_file" "$FIRST_SEEN" "$now" "$new_level" "$NOTIFY_COUNT"
    log "Escalation: ${alert_key} level=${new_level} count=${NOTIFY_COUNT} duration=${duration_min}m"
}

resolve_alert() {
    local alert_key="$1"
    local state_file="${STATE_DIR}/${alert_key}.state"
    if [[ -f "$state_file" ]]; then
        read_state "$state_file"
        local duration_min=$(( ($(date +%s) - FIRST_SEEN) / 60 ))
        send_webhook "✅ [RESOLVED] ${alert_key} 해결됨 (지속 ${duration_min}분, 알림 ${NOTIFY_COUNT}회)"
        rm -f "$state_file"
        log "Resolved: ${alert_key} (${duration_min}m, ${NOTIFY_COUNT} notifications)"
    fi
}

main() {
    mkdir -p "$STATE_DIR" "$(dirname "$LOG_FILE")"
    if [[ "${1:-}" == "--resolve" ]]; then
        [[ -z "${2:-}" ]] && { echo "Usage: $0 --resolve <alert_key>"; exit 1; }
        resolve_alert "$2"
    elif [[ $# -ge 3 ]]; then
        process_alert "$1" "$2" "$3"
    else
        echo "Usage: $0 <alert_key> <severity> <message>"
        echo "       $0 --resolve <alert_key>"
        exit 1
    fi
}

main "$@"
