#!/bin/bash
# ============================================================================
# 자율 복구 엔진 — healing-rules.json 기반 장애 감지 + 자동 복구
# watchdog에서 1분마다 호출됨
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../config/.env.mt" 2>/dev/null || true
[ -f "${SCRIPT_DIR}/../config/.env.mt.local" ] && source "${SCRIPT_DIR}/../config/.env.mt.local"

RULES_FILE="${SCRIPT_DIR}/healing-rules.json"
STATE_DIR="${STATE_DIR:-$HOME/.pillright-mt/state}/healing"
LOG_FILE="${LOG_DIR:-$HOME/.pillright-mt/logs}/healing-engine.log"
ESCALATION_SCRIPT="${SCRIPT_DIR}/../escalation/alert-escalation.sh"
PROJECT_DIR="${PROJECT_DIR:-$HOME/workspace/yakmeogeo}"
API_BASE="${API_BASE:-http://localhost:8000}"
DOMAIN="${DOMAIN:-pillright.com}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [HEALING] $1" | tee -a "$LOG_FILE"; }

escalate() {
    if [[ -x "$ESCALATION_SCRIPT" ]]; then
        "$ESCALATION_SCRIPT" "$1" "$2" "$3" || log "WARN: Escalation call failed for $1"
    else
        log "WARN: Escalation script not found: $ESCALATION_SCRIPT"
    fi
}

resolve() {
    if [[ -x "$ESCALATION_SCRIPT" ]]; then
        "$ESCALATION_SCRIPT" --resolve "$1" || true
    fi
}

check_cooldown() {
    local f="${STATE_DIR}/${1}.cooldown"
    [[ -f "$f" ]] || return 0
    local elapsed=$(( $(date +%s) - $(cat "$f") ))
    [[ $elapsed -ge $2 ]]
}

set_cooldown() { date +%s > "${STATE_DIR}/${1}.cooldown"; }

# --- 감지 함수들 ---
detect_http() {
    local url="${1//\$\{API_BASE\}/$API_BASE}"
    local expect="${2:-200}" timeout="${3:-10}" body_check="${4:-}"
    local code
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time "$timeout" "$url" 2>/dev/null) || code="000"
    [[ "$code" != "$expect" ]] && return 1
    if [[ -n "$body_check" ]]; then
        local resp; resp=$(curl -s --max-time "$timeout" "$url" 2>/dev/null) || resp=""
        echo "$resp" | grep -q "$body_check" && return 1
    fi
    return 0
}

detect_container() {
    local container="$1" cmd="${2:-}"
    local status; status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null) || status="not_found"
    [[ "$status" != "running" ]] && return 1
    [[ -n "$cmd" ]] && ! docker exec "$container" $cmd > /dev/null 2>&1 && return 1
    return 0
}

detect_disk() {
    local threshold="$1"
    local usage; usage=$(df -h / | awk 'NR==2 {gsub(/%/,""); print $5}')
    [[ "$usage" -ge "$threshold" ]]
}

detect_memory() {
    local threshold="$1" usage
    if [[ "$(uname)" == "Darwin" ]]; then
        usage=50  # macOS: 간략 체크
    else
        usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    fi
    [[ "$usage" -ge "$threshold" ]]
}

detect_ssl() {
    local domain="${1//\$\{DOMAIN\}/$DOMAIN}" warn_days="${2:-7}"
    [[ -z "$domain" ]] && return 0
    local expiry; expiry=$(echo | openssl s_client -servername "$domain" -connect "${domain}:443" 2>/dev/null \
        | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2) || return 0
    [[ -z "$expiry" ]] && return 0
    local exp_epoch; exp_epoch=$(date -d "$expiry" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry" +%s 2>/dev/null) || return 0
    local days_left=$(( (exp_epoch - $(date +%s)) / 86400 ))
    [[ $days_left -le $warn_days ]]
}

detect_stale_lock() {
    local lock="${1//\$\{PROJECT_DIR\}/$PROJECT_DIR}" max_min="${2:-120}"
    [[ ! -f "$lock" ]] && return 1
    local age_min
    if [[ "$(uname)" == "Darwin" ]]; then
        age_min=$(( ( $(date +%s) - $(stat -f%m "$lock") ) / 60 ))
    else
        age_min=$(( ( $(date +%s) - $(stat -c%Y "$lock") ) / 60 ))
    fi
    [[ $age_min -ge $max_min ]]
}

# --- 액션 실행 ---
do_action() {
    local type="$1" target="$2" wait="${3:-10}"
    case "$type" in
        restart_container)
            log "ACTION: restart ${target}"
            docker restart "$target" 2>>"$LOG_FILE" && sleep "$wait" || log "ERROR: restart ${target} failed"
            ;;
        restart_dependencies)
            for c in $(echo "$target" | tr ',' ' '); do
                c=$(echo "$c" | tr -d ' "[]')
                log "ACTION: restart dependency ${c}"
                docker restart "$c" 2>>"$LOG_FILE" || true
            done
            sleep "$wait"
            ;;
        shell_command)
            local cmd="${target//\$\{PROJECT_DIR\}/$PROJECT_DIR}"
            cmd="${cmd//\$\{LOG_DIR\}/${LOG_DIR:-$HOME/.pillright-mt/logs}}"
            log "ACTION: shell command"
            eval "$cmd" 2>>"$LOG_FILE" || log "ERROR: command failed"
            ;;
        full_stack_restart)
            log "ACTION: full stack restart"
            (cd "$PROJECT_DIR" && eval "$target") 2>>"$LOG_FILE"
            sleep "$wait"
            ;;
    esac
}

# --- 메인: JSON 룰 파싱 + 실행 ---
main() {
    mkdir -p "$STATE_DIR" "$(dirname "$LOG_FILE")"
    [[ ! -f "$RULES_FILE" ]] && { log "ERROR: Rules not found: $RULES_FILE"; exit 1; }

    local rule_count
    rule_count=$(python3 -c "import json; print(len(json.load(open('$RULES_FILE'))['rules']))" 2>/dev/null || echo "0")

    for i in $(seq 0 $((rule_count - 1))); do
        local rule_id desc detect_type cooldown alert_key severity
        rule_id=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r['id'])")
        desc=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r['description'])")
        detect_type=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r['detect']['type'])")
        alert_key=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r['escalation']['alert_key'])")
        severity=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r['escalation']['severity'])")
        cooldown=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(r.get('cooldown',300))")
        local detect_json=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(json.dumps(r['detect']))")

        # 감지
        local problem=false
        case "$detect_type" in
            http_check)
                local url=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('url',''))")
                local expect=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('expect_status',200))")
                local tout=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('timeout',10))")
                local body=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('expect_body_contains',''))")
                detect_http "$url" "$expect" "$tout" "$body" || problem=true
                ;;
            container_check)
                local ct=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('container',''))")
                local hcmd=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('health_cmd',''))")
                detect_container "$ct" "$hcmd" || problem=true
                ;;
            disk_check)
                local thr=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('threshold',90))")
                detect_disk "$thr" && problem=true
                ;;
            memory_check)
                local thr=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('threshold',90))")
                detect_memory "$thr" && problem=true
                ;;
            ssl_check)
                local dom=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('domain',''))")
                local wd=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('warn_days',7))")
                detect_ssl "$dom" "$wd" && problem=true
                ;;
            stale_lock)
                local lf=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('lock_file',''))")
                local ma=$(echo "$detect_json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('max_age_minutes',120))")
                detect_stale_lock "$lf" "$ma" && problem=true
                ;;
        esac

        # 정상 → 이전 장애 해소
        if [[ "$problem" == "false" ]]; then
            if [[ -f "${STATE_DIR}/${rule_id}.active" ]]; then
                rm -f "${STATE_DIR}/${rule_id}.active"
                resolve "$alert_key"
                log "RESOLVED: ${rule_id}"
            fi
            continue
        fi

        # 문제 감지
        log "DETECTED: ${rule_id} - ${desc}"
        touch "${STATE_DIR}/${rule_id}.active"

        if ! check_cooldown "$rule_id" "$cooldown"; then
            escalate "$alert_key" "$severity" "${desc} (쿨다운 중)"
            continue
        fi

        # 액션 순차 실행
        local act_count=$(python3 -c "import json; r=json.load(open('$RULES_FILE'))['rules'][$i]; print(len(r['actions']))")
        for j in $(seq 0 $((act_count - 1))); do
            local atype=$(python3 -c "import json; a=json.load(open('$RULES_FILE'))['rules'][$i]['actions'][$j]; print(a['action'])")
            local await=$(python3 -c "import json; a=json.load(open('$RULES_FILE'))['rules'][$i]['actions'][$j]; print(a.get('wait_after',10))")
            local atarget
            case "$atype" in
                restart_container) atarget=$(python3 -c "import json; a=json.load(open('$RULES_FILE'))['rules'][$i]['actions'][$j]; print(a['target'])") ;;
                restart_dependencies) atarget=$(python3 -c "import json; a=json.load(open('$RULES_FILE'))['rules'][$i]['actions'][$j]; print(','.join(a['targets']))") ;;
                shell_command|full_stack_restart) atarget=$(python3 -c "import json; a=json.load(open('$RULES_FILE'))['rules'][$i]['actions'][$j]; print(a['command'])") ;;
                *) continue ;;
            esac

            do_action "$atype" "$atarget" "$await"

            # 복구 확인
            if [[ "$detect_type" == "http_check" || "$detect_type" == "container_check" ]]; then
                sleep 3
                local healed=false
                case "$detect_type" in
                    http_check) detect_http "$url" "$expect" "$tout" "" && healed=true ;;
                    container_check) detect_container "$ct" "$hcmd" && healed=true ;;
                esac
                if [[ "$healed" == "true" ]]; then
                    log "HEALED: ${rule_id} after action #$((j+1))"
                    set_cooldown "$rule_id"
                    resolve "$alert_key"
                    break
                fi
            fi
        done

        # 복구 못했으면 에스컬레이션
        if [[ -f "${STATE_DIR}/${rule_id}.active" ]]; then
            set_cooldown "$rule_id"
            escalate "$alert_key" "$severity" "${desc} (자동 복구 시도 완료, 수동 확인 필요)"
        fi
    done
}

main "$@"
