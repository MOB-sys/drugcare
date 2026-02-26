import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";
import { SmartAppBanner } from "@/components/common/SmartAppBanner";

const GA_ID = process.env.NEXT_PUBLIC_GA_ID;
const ADSENSE_ID = process.env.NEXT_PUBLIC_ADSENSE_ID;

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
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen flex flex-col bg-[var(--color-bg)] text-gray-900 antialiased">
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
      </body>
    </html>
  );
}
