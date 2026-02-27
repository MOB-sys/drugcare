import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";
import { SmartAppBanner } from "@/components/common/SmartAppBanner";

const GA_ID = process.env.NEXT_PUBLIC_GA_ID;
const ADSENSE_ID = process.env.NEXT_PUBLIC_ADSENSE_ID;
const NAVER_VERIFY = process.env.NEXT_PUBLIC_NAVER_SITE_VERIFICATION;
const KAKAO_JS_KEY = process.env.NEXT_PUBLIC_KAKAO_JS_KEY;

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#1B3A5C" },
    { media: "(prefers-color-scheme: dark)", color: "#0F172A" },
  ],
};

export const metadata: Metadata = {
  title: {
    default: "MediCheck — 약/영양제 상호작용 체커",
    template: "%s | MediCheck",
  },
  description:
    "이 약이랑 이 영양제, 같이 먹어도 돼? 3초 만에 확인하는 복약 안전 체커. 의약품·건강기능식품 상호작용 정보를 무료로 확인하세요.",
  keywords: [
    "약 상호작용",
    "영양제 상호작용",
    "복약 체크",
    "약물 상호작용 확인",
    "건강기능식품",
    "MediCheck",
    "메디체크",
  ],
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "MediCheck",
    images: [
      {
        url: `${process.env.NEXT_PUBLIC_SITE_URL || "https://yakmeogeo.com"}/api/og?title=MediCheck&type=default`,
        width: 1200,
        height: 630,
        alt: "MediCheck — 약/영양제 상호작용 체커",
      },
    ],
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "MediCheck",
  },
  formatDetection: {
    telephone: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <head>
        {/* 네이버 서치어드바이저 사이트 소유 확인 */}
        {NAVER_VERIFY && <meta name="naver-site-verification" content={NAVER_VERIFY} />}
        {/* Pretendard 폰트 preload — CLS 방지 */}
        <link
          rel="preload"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/woff2/PretendardVariable.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        {/* DNS prefetch for external resources */}
        <link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />
        <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
        {/* 다크모드 깜빡임 방지 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('medicheck_theme');var d=t==='dark'||(t!=='light'&&window.matchMedia('(prefers-color-scheme:dark)').matches);if(d)document.documentElement.classList.add('dark')}catch(e){}})()`,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-[var(--color-bg)] text-[var(--color-text)] antialiased">
        <Header />
        <DisclaimerBanner />
        <SmartAppBanner />
        <main className="flex-1">{children}</main>
        <Footer />

        {/* Google Analytics 4 */}
        {GA_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
              strategy="afterInteractive"
            />
            <Script id="ga4-init" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${GA_ID}');
              `}
            </Script>
          </>
        )}

        {/* Google AdSense */}
        {ADSENSE_ID && (
          <Script
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_ID}`}
            crossOrigin="anonymous"
            strategy="lazyOnload"
          />
        )}

        {/* Kakao SDK — 카카오톡 공유 */}
        {KAKAO_JS_KEY && (
          <>
            <Script
              src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"
              crossOrigin="anonymous"
              strategy="afterInteractive"
            />
            <Script id="kakao-init" strategy="afterInteractive">
              {`(function check(){if(window.Kakao&&!window.Kakao.isInitialized()){window.Kakao.init('${KAKAO_JS_KEY}')}else{setTimeout(check,200)}})();`}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
