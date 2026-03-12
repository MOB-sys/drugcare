#!/bin/bash
# ============================================================================
# 요청 모니터링 — Nginx 로그 기반 이상 요청 탐지
# watchdog에서 주기적으로 호출하거나 독립 실행 가능
#
# 사용법:
#   ./request-monitor.sh [access_log_path]
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../config/.env.mt" 2>/dev/null || true
[ -f "${SCRIPT_DIR}/../config/.env.mt.local" ] && source "${SCRIPT_DIR}/../config/.env.mt.local"

ACCESS_LOG="${1:-/var/log/nginx/access.log}"
REPORT_DIR="${SCRIPT_DIR}/reports"
STATE_DIR="${STATE_DIR:-$HOME/.pillright-mt/state}/security"
LOG_FILE="${LOG_DIR:-$HOME/.pillright-mt/logs}/request-monitor.log"
ESCALATION_SCRIPT="${SCRIPT_DIR}/../escalation/alert-escalation.sh"

# 탐지 임계값
RATE_THRESHOLD="${RATE_THRESHOLD:-100}"        # IP당 분당 요청 수
ERROR_THRESHOLD="${ERROR_THRESHOLD:-50}"        # 분당 4xx/5xx 에러 수
SCAN_THRESHOLD="${SCAN_THRESHOLD:-10}"          # 분당 스캔 패턴 횟수

mkdir -p "$REPORT_DIR" "$STATE_DIR" "$(dirname "$LOG_FILE")"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [REQ-MON] $1" | tee -a "$LOG_FILE"; }

escalate() {
    if [[ -x "$ESCALATION_SCRIPT" ]]; then
        "$ESCALATION_SCRIPT" "$1" "$2" "$3" || log "WARN: Escalation failed for $1"
    else
        log "ALERT: [$2] $3"
    fi
}

resolve() {
    if [[ -x "$ESCALATION_SCRIPT" ]]; then
        "$ESCALATION_SCRIPT" --resolve "$1" || true
    fi
}

# --- 로그 파일 확인 ---

if [[ ! -f "$ACCESS_LOG" ]]; then
    log "SKIP: Access log not found: $ACCESS_LOG"
    exit 0
fi

# --- 1. IP별 요청 빈도 분석 (DDoS/brute-force 탐지) ---

log "Analyzing request rates..."

# 최근 로그에서 IP 추출 + 카운트 (Nginx combined format 기준)
HIGH_RATE_IPS=$(awk -v threshold="$RATE_THRESHOLD" '
{
    ip = $1
    count[ip]++
}
END {
    for (ip in count) {
        if (count[ip] >= threshold) {
            printf "%s %d\n", ip, count[ip]
        }
    }
}' <(tail -10000 "$ACCESS_LOG" 2>/dev/null) | sort -k2 -rn)

if [[ -n "$HIGH_RATE_IPS" ]]; then
    log "HIGH RATE IPs detected:"
    echo "$HIGH_RATE_IPS" | while read -r ip count; do
        log "  ${ip}: ${count} requests"
    done
    escalate "high_request_rate" "WARNING" "비정상 요청 빈도 감지: $(echo "$HIGH_RATE_IPS" | head -1)"
else
    resolve "high_request_rate"
fi

# --- 2. 에러율 분석 ---

log "Analyzing error rates..."

ERROR_COUNT=$(tail -5000 "$ACCESS_LOG" 2>/dev/null \
    | awk '$9 ~ /^[45][0-9][0-9]$/ {count++} END {print count+0}')

if [[ "$ERROR_COUNT" -ge "$ERROR_THRESHOLD" ]]; then
    log "HIGH ERROR RATE: ${ERROR_COUNT} errors in recent logs"

    # 에러 유형 분류
    ERROR_BREAKDOWN=$(tail -5000 "$ACCESS_LOG" 2>/dev/null \
        | awk '$9 ~ /^[45][0-9][0-9]$/ {count[$9]++} END {for(c in count) printf "  %s: %d\n", c, count[c]}' \
        | sort -k2 -rn)
    log "Error breakdown:"
    log "$ERROR_BREAKDOWN"

    escalate "high_error_rate" "WARNING" "에러율 급증: ${ERROR_COUNT}건 (임계값 ${ERROR_THRESHOLD})"
else
    resolve "high_error_rate"
fi

# --- 3. 공격 패턴 탐지 ---

log "Scanning for attack patterns..."

# SQL Injection 패턴
SQLI_COUNT=$(tail -10000 "$ACCESS_LOG" 2>/dev/null \
    | grep -ciE "(union.*select|or.*1.*=.*1|drop.*table|insert.*into|;.*--)" || echo "0")

# Path Traversal 패턴
TRAVERSAL_COUNT=$(tail -10000 "$ACCESS_LOG" 2>/dev/null \
    | grep -c '\.\.\/' || echo "0")

# Scanner/Bot 패턴
SCANNER_COUNT=$(tail -10000 "$ACCESS_LOG" 2>/dev/null \
    | grep -ciE "(wp-admin|wp-login|phpmyadmin|\.asp|\.php|\.cgi|/admin|/manager|xmlrpc)" || echo "0")

# XSS 패턴
XSS_COUNT=$(tail -10000 "$ACCESS_LOG" 2>/dev/null \
    | grep -ciE "(<script|javascript:|on(error|load|click)=)" || echo "0")

TOTAL_ATTACKS=$((SQLI_COUNT + TRAVERSAL_COUNT + SCANNER_COUNT + XSS_COUNT))

if [[ "$TOTAL_ATTACKS" -ge "$SCAN_THRESHOLD" ]]; then
    log "ATTACK PATTERNS DETECTED:"
    log "  SQL Injection: ${SQLI_COUNT}"
    log "  Path Traversal: ${TRAVERSAL_COUNT}"
    log "  Scanner/Bot: ${SCANNER_COUNT}"
    log "  XSS: ${XSS_COUNT}"

    # 공격 IP 추출
    ATTACK_IPS=$(tail -10000 "$ACCESS_LOG" 2>/dev/null \
        | grep -iE "(union.*select|\.\.\/|wp-admin|<script)" \
        | awk '{print $1}' | sort | uniq -c | sort -rn | head -5)
    if [[ -n "$ATTACK_IPS" ]]; then
        log "Top attack source IPs:"
        log "$ATTACK_IPS"
    fi

    escalate "attack_detected" "CRITICAL" "공격 패턴 탐지: SQLi=${SQLI_COUNT}, Traversal=${TRAVERSAL_COUNT}, Scanner=${SCANNER_COUNT}, XSS=${XSS_COUNT}"
else
    resolve "attack_detected"
fi

# --- 4. 비정상 User-Agent ---

log "Checking suspicious user agents..."

SUS_UA=$(tail -5000 "$ACCESS_LOG" 2>/dev/null \
    | grep -ciE '(sqlmap|nikto|nmap|masscan|dirbuster|gobuster|wpscan|nuclei|hydra)' || echo "0")

if [[ "$SUS_UA" -gt 0 ]]; then
    log "SUSPICIOUS USER AGENTS: ${SUS_UA} requests"
    escalate "suspicious_ua" "WARNING" "보안 스캐너 User-Agent 탐지: ${SUS_UA}건"
else
    resolve "suspicious_ua"
fi

# --- 상태 저장 ---

cat > "${STATE_DIR}/monitor_status.json" << EOF
{
    "timestamp": $(date +%s),
    "high_rate_ips": $(echo "$HIGH_RATE_IPS" | wc -l | tr -d ' '),
    "error_count": $ERROR_COUNT,
    "attack_patterns": $TOTAL_ATTACKS,
    "suspicious_ua": $SUS_UA
}
EOF

log "Monitoring complete."
