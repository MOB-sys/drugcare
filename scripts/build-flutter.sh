#!/usr/bin/env bash
# ==============================================================================
# 약먹어 Flutter 프로덕션 빌드 스크립트
# Usage: ./scripts/build-flutter.sh [dev|prod] [android|ios|both]
# ==============================================================================
set -euo pipefail

ENV="${1:-dev}"
PLATFORM="${2:-android}"
FRONTEND_DIR="$(cd "$(dirname "$0")/../src/frontend" && pwd)"

# --- 환경 파일 로드 ---
if [ "$ENV" = "prod" ]; then
    ENV_FILE="$FRONTEND_DIR/.env.prod"
    if [ ! -f "$ENV_FILE" ]; then
        echo "❌ $ENV_FILE 파일이 없습니다."
        echo "   cp src/frontend/.env.prod.example src/frontend/.env.prod 후 값을 채워주세요."
        exit 1
    fi
    # shellcheck source=/dev/null
    source "$ENV_FILE"
    echo "📦 프로덕션 빌드 ($PLATFORM)"
else
    # dev: 테스트 ID 사용 (dart-define 없이 defaultValue 적용)
    echo "🔧 개발 빌드 ($PLATFORM)"
fi

cd "$FRONTEND_DIR"

# --- dart-define 구성 ---
DART_DEFINES=""
if [ "$ENV" = "prod" ]; then
    DART_DEFINES="--dart-define=API_BASE_URL=${API_BASE_URL:-https://api.pillright.com}"
    [ -n "${ADMOB_ANDROID_BANNER:-}" ]       && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_ANDROID_BANNER=$ADMOB_ANDROID_BANNER"
    [ -n "${ADMOB_ANDROID_INTERSTITIAL:-}" ] && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_ANDROID_INTERSTITIAL=$ADMOB_ANDROID_INTERSTITIAL"
    [ -n "${ADMOB_ANDROID_NATIVE:-}" ]       && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_ANDROID_NATIVE=$ADMOB_ANDROID_NATIVE"
    [ -n "${ADMOB_IOS_BANNER:-}" ]           && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_IOS_BANNER=$ADMOB_IOS_BANNER"
    [ -n "${ADMOB_IOS_INTERSTITIAL:-}" ]     && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_IOS_INTERSTITIAL=$ADMOB_IOS_INTERSTITIAL"
    [ -n "${ADMOB_IOS_NATIVE:-}" ]           && DART_DEFINES="$DART_DEFINES --dart-define=ADMOB_IOS_NATIVE=$ADMOB_IOS_NATIVE"
fi

# --- Android 빌드 ---
build_android() {
    echo "🤖 Android App Bundle 빌드 중..."
    # shellcheck disable=SC2086
    flutter build appbundle --release $DART_DEFINES
    echo "✅ Android 빌드 완료: build/app/outputs/bundle/release/app-release.aab"
}

# --- iOS 빌드 ---
build_ios() {
    echo "🍎 iOS 빌드 중..."
    # shellcheck disable=SC2086
    flutter build ios --release --no-codesign $DART_DEFINES
    echo "✅ iOS 빌드 완료: build/ios/iphoneos/Runner.app"
    echo "   Xcode에서 Archive → App Store 업로드를 진행하세요."
}

# --- 실행 ---
case "$PLATFORM" in
    android) build_android ;;
    ios)     build_ios ;;
    both)    build_android; build_ios ;;
    *)       echo "❌ 지원하지 않는 플랫폼: $PLATFORM (android|ios|both)"; exit 1 ;;
esac

echo "🎉 빌드 완료!"
