#!/bin/bash
# pre-deploy-check.sh — 배포 전 설정 일관성 + 연결 검증
# 사용: ssh로 서버에서 실행 또는 CI에서 호출
set -euo pipefail

COMPOSE_FILE="${1:-docker-compose.prod.yml}"
ENV_FILE="${2:-.env}"
FAIL=0

echo "=== 배포 전 검증 시작 ==="

# 1) .env 파일 존재 확인
if [ ! -f "$ENV_FILE" ]; then
  echo "FAIL: $ENV_FILE 파일이 없습니다"
  exit 1
fi

# 2) 필수 환경변수 확인
REQUIRED_VARS="DATABASE_URL REDIS_URL APP_ENV"
for var in $REQUIRED_VARS; do
  if ! grep -q "^${var}=" "$ENV_FILE"; then
    echo "FAIL: $ENV_FILE에 ${var}가 없습니다"
    FAIL=1
  fi
done

# 3) DB 비밀번호 일관성 — .env vs docker-compose
ENV_DB_PASS=$(grep '^DATABASE_URL=' "$ENV_FILE" | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')
COMPOSE_DB_PASS=$(grep 'DB_PASSWORD' "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2)
if [ -n "$COMPOSE_DB_PASS" ] && [ "$ENV_DB_PASS" != "$COMPOSE_DB_PASS" ]; then
  echo "FAIL: DATABASE_URL 비밀번호와 DB_PASSWORD가 다릅니다"
  FAIL=1
fi

# 4) Redis 비밀번호 일관성
ENV_REDIS_PASS=$(grep '^REDIS_URL=' "$ENV_FILE" | sed 's/.*:\/\/:\([^@]*\)@.*/\1/')
REDIS_PASS_VAR=$(grep '^REDIS_PASSWORD=' "$ENV_FILE" 2>/dev/null | cut -d= -f2)
if [ -n "$REDIS_PASS_VAR" ] && [ "$ENV_REDIS_PASS" != "$REDIS_PASS_VAR" ]; then
  echo "FAIL: REDIS_URL 비밀번호와 REDIS_PASSWORD가 다릅니다"
  FAIL=1
fi

# 5) Docker 컨테이너 상태 확인
if command -v docker &>/dev/null; then
  for svc in yakmeogeo-db yakmeogeo-redis; do
    STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$svc" 2>/dev/null || echo "missing")
    if [ "$STATUS" != "healthy" ]; then
      echo "FAIL: $svc 상태 = $STATUS (healthy 필요)"
      FAIL=1
    fi
  done
fi

# 6) 실제 DB 연결 테스트
if command -v docker &>/dev/null && docker ps -q -f name=yakmeogeo-db | grep -q .; then
  if docker exec yakmeogeo-db pg_isready -U yakmeogeo -q 2>/dev/null; then
    echo "OK: PostgreSQL 연결 가능"
  else
    echo "FAIL: PostgreSQL 연결 불가"
    FAIL=1
  fi
fi

# 7) 프로덕션 모드 확인
APP_ENV=$(grep '^APP_ENV=' "$ENV_FILE" | cut -d= -f2)
if [ "$APP_ENV" != "production" ]; then
  echo "WARN: APP_ENV=$APP_ENV (production 아님)"
fi

# 8) Nginx → backend 네트워크 연결 확인
if command -v docker &>/dev/null && docker ps -q -f name=yakmeogeo-nginx | grep -q .; then
  if docker exec yakmeogeo-nginx ping -c 1 -W 2 backend >/dev/null 2>&1; then
    echo "OK: Nginx → backend 네트워크 정상"
  else
    echo "FAIL: Nginx에서 backend를 찾을 수 없음 (네트워크 분리됨)"
    FAIL=1
  fi
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "=== 모든 검증 통과 — 배포 가능 ==="
else
  echo "=== 검증 실패 — 배포 중단 ==="
  exit 1
fi
