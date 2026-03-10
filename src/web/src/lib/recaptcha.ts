/**
 * Google reCAPTCHA v3 유틸리티.
 *
 * - 스크립트를 지연 로딩하여 필요할 때만 불러옵니다.
 * - NEXT_PUBLIC_RECAPTCHA_SITE_KEY 환경변수가 없으면 graceful 하게 무시합니다.
 * - npm 패키지 없이 script tag 방식으로 동작합니다.
 */

declare global {
  interface Window {
    grecaptcha: {
      ready: (cb: () => void) => void;
      execute: (siteKey: string, options: { action: string }) => Promise<string>;
    };
  }
}

const SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY ?? "";

let scriptLoaded = false;
let scriptLoading: Promise<void> | null = null;

/** reCAPTCHA 스크립트를 지연 로딩합니다. 이미 로딩 중이면 기존 Promise를 반환합니다. */
function loadScript(): Promise<void> {
  if (scriptLoaded) return Promise.resolve();
  if (scriptLoading) return scriptLoading;

  scriptLoading = new Promise<void>((resolve, reject) => {
    if (typeof window === "undefined") {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src = `https://www.google.com/recaptcha/api.js?render=${SITE_KEY}`;
    script.async = true;
    script.defer = true;

    script.onload = () => {
      scriptLoaded = true;
      resolve();
    };
    script.onerror = () => {
      scriptLoading = null;
      reject(new Error("reCAPTCHA 스크립트 로딩 실패"));
    };

    document.head.appendChild(script);
  });

  return scriptLoading;
}

/**
 * reCAPTCHA v3 토큰을 발급받습니다.
 *
 * @param action - reCAPTCHA action 이름 (예: "submit_review", "submit_feedback")
 * @returns 토큰 문자열, 또는 환경변수 미설정/에러 시 null
 */
export async function executeRecaptcha(action: string): Promise<string | null> {
  if (!SITE_KEY) return null;
  if (typeof window === "undefined") return null;

  try {
    await loadScript();

    return await new Promise<string>((resolve, reject) => {
      window.grecaptcha.ready(() => {
        window.grecaptcha
          .execute(SITE_KEY, { action })
          .then(resolve)
          .catch(reject);
      });
    });
  } catch {
    // reCAPTCHA 실패 시에도 폼 제출은 허용 (graceful degradation)
    console.warn("reCAPTCHA 토큰 발급 실패, 토큰 없이 진행합니다.");
    return null;
  }
}
