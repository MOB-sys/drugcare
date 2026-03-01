#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# PillRight — Let's Encrypt SSL 초기 발급 스크립트
# ==============================================================================
# 사용법: bash scripts/deploy/init-ssl.sh [도메인] [이메일]
# 예시:   bash scripts/deploy/init-ssl.sh api.pillright.com support@pillright.com
# ==============================================================================

DOMAIN="${1:-api.pillright.com}"
EMAIL="${2:-support@pillright.com}"

echo "=== SSL 인증서 발급: ${DOMAIN} ==="

# 1. nginx를 HTTP-only 모드로 먼저 시작 (임시 설정)
echo ">>> 임시 nginx 시작 (HTTP only)..."
cat > /tmp/nginx-acme.conf <<'CONF'
server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'ssl-init';
        add_header Content-Type text/plain;
    }
}
CONF

docker run -d --name ssl-nginx \
    -p 80:80 \
    -v /tmp/nginx-acme.conf:/etc/nginx/conf.d/default.conf:ro \
    -v certbot-var:/var/www/certbot \
    nginx:1.25-alpine

echo ">>> 3초 대기..."
sleep 3

# 2. Certbot으로 인증서 발급
echo ">>> Let's Encrypt 인증서 발급 중..."
docker run --rm \
    -v certbot-etc:/etc/letsencrypt \
    -v certbot-var:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email \
    -d "${DOMAIN}"

# 3. 임시 nginx 정리
echo ">>> 임시 nginx 정리..."
docker stop ssl-nginx && docker rm ssl-nginx

echo "=== SSL 인증서 발급 완료! ==="
echo "인증서 위치: /etc/letsencrypt/live/${DOMAIN}/"
echo ""
echo "다음 단계: bash scripts/deploy/deploy.sh"
