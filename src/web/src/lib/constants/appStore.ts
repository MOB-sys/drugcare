/** App Store / Play Store URL 유틸리티 + UTM 추적 */

const IOS_APP_ID = process.env.NEXT_PUBLIC_IOS_APP_ID || "0000000000";
const ANDROID_PACKAGE = "com.yakmeogeo.app";

const APP_STORE_BASE = `https://apps.apple.com/kr/app/pillright/id${IOS_APP_ID}`;
const PLAY_STORE_BASE = `https://play.google.com/store/apps/details?id=${ANDROID_PACKAGE}&hl=ko`;

export type Platform = "ios" | "android";

/** UTM 파라미터가 포함된 스토어 URL 생성 */
export function getStoreUrl(
  platform: Platform,
  source: string,
  medium: string,
  campaign?: string,
): string {
  const base = platform === "ios" ? APP_STORE_BASE : PLAY_STORE_BASE;
  const separator = base.includes("?") ? "&" : "?";
  const params = new URLSearchParams({
    utm_source: source,
    utm_medium: medium,
  });
  if (campaign) params.set("utm_campaign", campaign);
  return `${base}${separator}${params.toString()}`;
}

/** UA 기반으로 플랫폼을 감지하여 스토어 URL 반환 (클라이언트 전용) */
export function getStoreUrlForPlatform(medium: string): string {
  if (typeof navigator === "undefined") {
    return getStoreUrl("android", "website", medium);
  }
  const isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  return getStoreUrl(
    isIOS ? "ios" : "android",
    "website",
    medium,
  );
}
