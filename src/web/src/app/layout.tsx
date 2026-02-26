import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/common/Header";
import { Footer } from "@/components/common/Footer";
import { DisclaimerBanner } from "@/components/common/DisclaimerBanner";

export const metadata: Metadata = {
  title: {
    default: "약먹어 — 약/영양제 상호작용 체커",
    template: "%s | 약먹어",
  },
  description:
    "이 약이랑 이 영양제, 같이 먹어도 돼? 3초 만에 확인하는 복약 안전 체커. 의약품·건강기능식품 상호작용 정보를 무료로 확인하세요.",
  keywords: [
    "약 상호작용",
    "영양제 상호작용",
    "복약 체크",
    "약물 상호작용 확인",
    "건강기능식품",
  ],
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "약먹어",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
        <Header />
        <DisclaimerBanner />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
