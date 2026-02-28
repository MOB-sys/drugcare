import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";

export const metadata: Metadata = {
  title: "문의하기",
  description: "PillRight 서비스에 대한 문의, 오류 신고, 데이터 수정 요청 등을 보내주세요.",
};

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "약물 정보는 어디서 가져오나요?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "식품의약품안전처 의약품안전나라 및 건강기능식품 정보 공공 API에서 수집합니다. 정기적으로 데이터를 업데이트하고 있습니다.",
      },
    },
    {
      "@type": "Question",
      name: "상호작용 정보는 정확한가요?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "공공 데이터와 AI 분석을 기반으로 제공됩니다. 다만, 이 정보는 참고용이며 의사/약사의 전문적 판단을 대체하지 않습니다. 실제 복용 결정은 반드시 전문가와 상담하세요.",
      },
    },
    {
      "@type": "Question",
      name: "회원가입이 필요한가요?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "아닙니다. PillRight는 회원가입 없이 모든 기능을 이용할 수 있습니다. 복약함 데이터는 기기에 저장됩니다.",
      },
    },
  ],
};

export default function ContactPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "문의하기" },
        ]}
      />

      <section className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-2">문의하기</h1>
        <p className="text-[var(--color-text-secondary)] mb-8">
          PillRight 서비스에 대한 문의사항이나 피드백을 보내주세요.
        </p>

        <div className="mb-8">
          <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="font-semibold text-[var(--color-text)] mb-1">이메일 문의</h2>
            <p className="text-sm text-[var(--color-text-secondary)] mb-3">서비스 이용, 기능 제안, 데이터 오류 신고 등 모든 문의</p>
            <a
              href="mailto:support@pillright.com"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--color-primary)] hover:underline"
            >
              support@pillright.com
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-6 mb-8">
          <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-4">자주 묻는 질문</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-[var(--color-text)] mb-1">약물 정보는 어디서 가져오나요?</h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                식품의약품안전처 의약품안전나라 및 건강기능식품 정보 공공 API에서 수집합니다. 정기적으로 데이터를 업데이트하고 있습니다.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-[var(--color-text)] mb-1">상호작용 정보는 정확한가요?</h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                공공 데이터와 AI 분석을 기반으로 제공됩니다. 다만, 이 정보는 참고용이며 의사/약사의 전문적 판단을 대체하지 않습니다. 실제 복용 결정은 반드시 전문가와 상담하세요.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-[var(--color-text)] mb-1">회원가입이 필요한가요?</h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                아닙니다. PillRight는 회원가입 없이 모든 기능을 이용할 수 있습니다. 복약함 데이터는 기기에 저장됩니다.
              </p>
            </div>
          </div>
        </div>

        <AdBanner slot="legal-bottom" format="auto" />

        {/* 추가 안내 */}
        <div className="text-center text-sm text-[var(--color-text-muted)]">
          <p className="mb-2">응답까지 영업일 기준 1~2일이 소요될 수 있습니다.</p>
          <p>
            서비스 이용에 대한 자세한 내용은{" "}
            <Link href="/terms" className="text-[var(--color-primary)] hover:underline">이용약관</Link>
            {" "}및{" "}
            <Link href="/privacy" className="text-[var(--color-primary)] hover:underline">개인정보처리방침</Link>
            을 참고해주세요.
          </p>
        </div>
      </section>
    </>
  );
}
