#!/bin/bash
# ============================================================================
# DB 자동 백업 시스템
# pg_dump 기반 백업 + 로컬 보관 + 선택적 S3 업로드
# watchdog에서 24시간마다 호출됨
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/../config/.env.mt" 2>/dev/null || true
[ -f "${SCRIPT_DIR}/../config/.env.mt.local" ] && source "${SCRIPT_DIR}/../config/.env.mt.local"

# 기본값
DB_CONTAINER="${DB_CONTAINER:-yakmeogeo-db}"
DB_NAME="${DB_NAME:-yakmeogeo}"
DB_USER="${DB_USER:-yakmeogeo}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/.pillright-mt/backups/db}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-yakmeogeo/db-backups}"
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"
LOG_FILE="${LOG_DIR:-$HOME/.pillright-mt/logs}/db-backup.log"

ESCALATION_SCRIPT="${SCRIPT_DIR}/../escalation/alert-escalation.sh"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [BACKUP] $1" | tee -a "$LOG_FILE"
}

alert() {
    local level="$1" message="$2"
    log "[${level}] ${message}"

    # 에스컬레이션 시스템이 있으면 위임
    if [[ -x "$ESCALATION_SCRIPT" ]]; then
        local severity="WARNING"
        [[ "$level" == "ERROR" ]] && severity="CRITICAL"
        [[ "$level" == "OK" ]] && severity="INFO"
        "$ESCALATION_SCRIPT" "db_backup" "$severity" "$message" 2>/dev/null || true
        [[ "$level" == "OK" ]] && "$ESCALATION_SCRIPT" --resolve "db_backup" 2>/dev/null || true
        return
    fi

    # 폴백: 직접 webhook
    if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
        local emoji="⚠️"
        [[ "$level" == "ERROR" ]] && emoji="🔴"
        [[ "$level" == "OK" ]] && emoji="✅"
        curl -s -X POST "$ALERT_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"${emoji} [DB Backup] ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

cleanup_old_backups() {
    local deleted_count=0
    if [[ -d "$BACKUP_DIR" ]]; then
        deleted_count=$(find "$BACKUP_DIR" -name "*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -print -delete 2>/dev/null | wc -l | tr -d ' ')
    fi
    log "Old backups cleaned: ${deleted_count} files (>${BACKUP_RETENTION_DAYS} days)"
}

upload_to_s3() {
    local file="$1"
    if [[ -z "$S3_BUCKET" ]]; then
        log "S3 upload skipped (S3_BUCKET not set)"
        return 0
    fi
    if ! command -v aws &>/dev/null; then
        log "WARN: aws CLI not found, skipping S3 upload"
        return 1
    fi
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/$(basename "$file")"
    if aws s3 cp "$file" "$s3_path" --quiet 2>>"$LOG_FILE"; then
        log "S3 upload OK: ${s3_path}"
    else
        alert "ERROR" "S3 upload failed: ${s3_path}"
        return 1
    fi
}

verify_backup() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        alert "ERROR" "Backup file not found: ${file}"
        return 1
    fi
    local size
    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    if [[ "$size" -lt 1024 ]]; then
        alert "ERROR" "Backup too small (${size} bytes): ${file}"
        return 1
    fi
    if ! gzip -t "$file" 2>/dev/null; then
        alert "ERROR" "Backup corrupted (gzip test failed): ${file}"
        return 1
    fi
    local size_mb
    size_mb=$(echo "scale=2; ${size}/1048576" | bc 2>/dev/null || echo "${size} bytes")
    log "Backup verified: ${size_mb}MB"
    return 0
}

main() {
    log "========== DB Backup Start =========="
    mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

    local container_status
    container_status=$(docker inspect --format='{{.State.Status}}' "$DB_CONTAINER" 2>/dev/null || echo "not_found")
    if [[ "$container_status" != "running" ]]; then
        alert "ERROR" "DB container '${DB_CONTAINER}' is not running (status: ${container_status})"
        exit 1
    fi

    log "Running pg_dump..."
    if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" \
        --no-owner --no-privileges --clean --if-exists \
        2>>"$LOG_FILE" | gzip > "$BACKUP_FILE"; then
        log "pg_dump completed: $(basename "$BACKUP_FILE")"
    else
        alert "ERROR" "pg_dump failed for ${DB_NAME}"
        rm -f "$BACKUP_FILE"
        exit 1
    fi

    if ! verify_backup "$BACKUP_FILE"; then
        rm -f "$BACKUP_FILE"
        exit 1
    fi

    upload_to_s3 "$BACKUP_FILE"
    cleanup_old_backups

    local backup_count
    backup_count=$(find "$BACKUP_DIR" -name "*.sql.gz" 2>/dev/null | wc -l | tr -d ' ')
    alert "OK" "Backup completed: $(basename "$BACKUP_FILE") (total: ${backup_count} files)"
    log "========== DB Backup Done =========="
}

main "$@"
