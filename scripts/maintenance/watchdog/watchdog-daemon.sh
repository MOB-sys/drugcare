#!/bin/bash
# ============================================================================
# Watchdog 데몬 — cron 대체 상시 감시 + 자율 복구 + 기존 ops 연동
#
# 사용법:
#   ./watchdog-daemon.sh start     # 데몬 시작
#   ./watchdog-daemon.sh stop      # 데몬 중지
#   ./watchdog-daemon.sh status    # 상태 확인
#   ./watchdog-daemon.sh restart   # 재시작
#   ./watchdog-daemon.sh run       # 포그라운드 실행 (디버그)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../config/.env.mt" 2>/dev/null || true
[ -f "${SCRIPT_DIR}/../config/.env.mt.local" ] && source "${SCRIPT_DIR}/../config/.env.mt.local"

DAEMON_NAME="pillright-watchdog"
PID_FILE="${PID_DIR:-$HOME/.pillright-mt/run}/${DAEMON_NAME}.pid"
LOG_FILE="${LOG_DIR:-$HOME/.pillright-mt/logs}/watchdog.log"
STATE_DIR="${STATE_DIR:-$HOME/.pillright-mt/state}/watchdog"

HEALING_SCRIPT="${SCRIPT_DIR}/../self-healing/healing-engine.sh"
BACKUP_SCRIPT="${SCRIPT_DIR}/../backup/db-backup.sh"
QA_SCRIPT="${QA_SCRIPT:-}"
DAILY_REPORT_SCRIPT="${DAILY_REPORT_SCRIPT:-}"

HEALING_INTERVAL="${HEALING_INTERVAL:-60}"
BACKUP_INTERVAL="${BACKUP_INTERVAL:-86400}"
QA_INTERVAL="${QA_INTERVAL:-21600}"
DAILY_REPORT_INTERVAL="${DAILY_REPORT_INTERVAL:-86400}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WATCHDOG] $1" | tee -a "$LOG_FILE"; }

ensure_dirs() { mkdir -p "$(dirname "$PID_FILE")" "$(dirname "$LOG_FILE")" "$STATE_DIR"; }

should_run() {
    local f="${STATE_DIR}/${1}.lastrun"
    [[ ! -f "$f" ]] && return 0
    [[ $(( $(date +%s) - $(cat "$f") )) -ge $2 ]]
}

mark_run() { date +%s > "${STATE_DIR}/${1}.lastrun"; }

run_task() {
    local name="$1" script="$2" interval="$3"
    [[ ! -x "$script" ]] && return
    if should_run "$name" "$interval"; then
        log "Task: ${name}"
        "$script" >> "$LOG_FILE" 2>&1 || log "ERROR: ${name} failed (exit=$?)"
        mark_run "$name"
    fi
}

watchdog_loop() {
    log "=========================================="
    log "Watchdog started (PID: $$)"
    log "  Healing:  ${HEALING_INTERVAL}s"
    log "  Backup:   ${BACKUP_INTERVAL}s"
    log "  QA:       ${QA_INTERVAL}s"
    log "  Report:   ${DAILY_REPORT_INTERVAL}s"
    [[ -n "$QA_SCRIPT" ]] && log "  QA script: ${QA_SCRIPT}"
    [[ -n "$DAILY_REPORT_SCRIPT" ]] && log "  Report script: ${DAILY_REPORT_SCRIPT}"
    log "=========================================="

    trap 'log "Shutting down..."; exit 0' SIGTERM SIGINT

    while true; do
        run_task "healing" "$HEALING_SCRIPT" "$HEALING_INTERVAL"
        run_task "db_backup" "$BACKUP_SCRIPT" "$BACKUP_INTERVAL"
        [[ -n "$QA_SCRIPT" ]] && run_task "qa_monitor" "$QA_SCRIPT" "$QA_INTERVAL"
        [[ -n "$DAILY_REPORT_SCRIPT" ]] && run_task "daily_report" "$DAILY_REPORT_SCRIPT" "$DAILY_REPORT_INTERVAL"

        echo "{\"pid\": $$, \"timestamp\": $(date +%s), \"status\": \"running\"}" > "${STATE_DIR}/heartbeat.json"
        sleep "$HEALING_INTERVAL"
    done
}

start_daemon() {
    ensure_dirs
    if [[ -f "$PID_FILE" ]]; then
        local old_pid; old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "Already running (PID: ${old_pid})"; exit 1
        fi
        rm -f "$PID_FILE"
    fi
    echo "Starting watchdog..."
    nohup "$0" run >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Watchdog started (PID: $!)"
    echo "Log: ${LOG_FILE}"
}

stop_daemon() {
    if [[ ! -f "$PID_FILE" ]]; then
        echo "Not running"
        return 0
    fi
    local pid; pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "Stopping (PID: ${pid})..."
        kill -SIGTERM "$pid"
        local c=0
        while kill -0 "$pid" 2>/dev/null && [[ $c -lt 10 ]]; do sleep 1; c=$((c+1)); done
        kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
        rm -f "$PID_FILE"
        echo "Stopped"
    else
        echo "Stale PID, cleaning up"; rm -f "$PID_FILE"
    fi
}

status_daemon() {
    [[ ! -f "$PID_FILE" ]] && { echo "STOPPED"; exit 1; }
    local pid; pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "RUNNING (PID: ${pid})"
        if [[ -f "${STATE_DIR}/heartbeat.json" ]]; then
            local age=$(( $(date +%s) - $(python3 -c "import json; print(json.load(open('${STATE_DIR}/heartbeat.json'))['timestamp'])" 2>/dev/null || echo "0") ))
            echo "  Heartbeat: ${age}s ago"
            [[ $age -gt $((HEALING_INTERVAL * 3)) ]] && echo "  WARNING: heartbeat stale"
        fi
        for task in healing db_backup qa_monitor daily_report; do
            local f="${STATE_DIR}/${task}.lastrun"
            [[ -f "$f" ]] && echo "  ${task}: $(( $(date +%s) - $(cat "$f") ))s ago"
        done
    else
        echo "DEAD (stale PID: ${pid})"; exit 1
    fi
}

case "${1:-help}" in
    start)   start_daemon ;;
    stop)    stop_daemon ;;
    restart) stop_daemon; start_daemon ;;
    status)  status_daemon ;;
    run)     ensure_dirs; echo $$ > "$PID_FILE"; watchdog_loop ;;
    *)       echo "Usage: $0 {start|stop|restart|status|run}" ;;
esac
