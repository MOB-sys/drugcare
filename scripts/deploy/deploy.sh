#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# PillRight — Production Deployment Script
# ==============================================================================

COMPOSE="docker compose -f docker-compose.prod.yml"
HEALTH_URL="http://localhost:8000/api/v1/health"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "=== PillRight 배포 시작 ==="

# 1. Check .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env 파일이 존재하지 않습니다."
    echo "  .env.production.example 을 참고하여 .env 파일을 생성하세요."
    exit 1
fi

# 2. Build images
echo ">>> Docker 이미지 빌드 중..."
$COMPOSE build

# 3. Start database services first for migrations
echo ">>> 데이터베이스 서비스 시작..."
$COMPOSE up -d postgres redis

echo ">>> 데이터베이스 준비 대기..."
sleep 10

# 4. Run Alembic migrations
echo ">>> Alembic 마이그레이션 실행..."
$COMPOSE run --rm backend alembic upgrade head

# 5. Start all services
echo ">>> 전체 서비스 시작..."
$COMPOSE up -d

# 6. Health check loop
echo ">>> 헬스체크 대기 중..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        echo ">>> 헬스체크 성공! (${i}/${MAX_RETRIES})"
        echo "=== 배포 완료 ==="
        $COMPOSE ps
        exit 0
    fi
    echo "  헬스체크 대기... (${i}/${MAX_RETRIES})"
    sleep $RETRY_INTERVAL
done

echo "ERROR: 헬스체크 실패 — 서비스가 응답하지 않습니다."
echo ">>> 로그 확인:"
$COMPOSE logs --tail=20 backend
exit 1
