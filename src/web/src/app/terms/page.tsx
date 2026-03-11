import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";

export const metadata: Metadata = {
  title: "이용약관",
  description: "약잘알 서비스 이용약관. 서비스 이용 조건, 면책사항, 약물 정보 제공 범위를 안내합니다.",
  alternates: { canonical: "/terms" },
};

export default function TermsPage() {
  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "이용약관" },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-6">이용약관</h1>
        <p className="text-sm text-[var(--color-text-muted)] mb-8">시행일: 2026년 2월 27일</p>

        <div className="space-y-8 text-[var(--color-text)] text-sm leading-relaxed break-keep">
          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제1조 (목적)</h2>
            <p>본 약관은 약잘알(이하 &quot;서비스&quot;)이 제공하는 약물·건강기능식품 정보 서비스의 이용 조건 및 절차에 관한 사항을 규정함을 목적으로 합니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제2조 (서비스의 내용)</h2>
            <p>서비스는 다음의 기능을 제공합니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>의약품 및 건강기능식품 상호작용 확인</li>
              <li>의약품·건강기능식품 상세 정보 제공</li>
              <li>복약함(복용 중인 약물 관리) 기능</li>
              <li>건강 관련 정보 콘텐츠 제공</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제3조 (면책사항)</h2>
            <div className="bg-[var(--color-primary-50)] rounded-xl p-4 border border-[var(--color-primary-100)]">
              <p className="font-semibold mb-2">중요 안내</p>
              <ul className="list-disc ml-5 space-y-1">
                <li>서비스에서 제공하는 정보는 <strong>참고용</strong>이며, 의학적 진단이나 치료를 대체하지 않습니다.</li>
                <li>약물 복용에 관한 결정은 반드시 <strong>의사 또는 약사</strong>와 상담 후 내려야 합니다.</li>
                <li>서비스는 식약처 공공데이터 기반으로 제공되며, 정보의 정확성을 보증하지 않습니다.</li>
                <li>서비스 이용으로 발생한 건강상의 문제에 대해 서비스 제공자는 책임을 지지 않습니다.</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제4조 (이용자의 의무)</h2>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>이용자는 서비스를 통해 얻은 정보를 의료 전문가의 조언 없이 단독으로 의료적 결정에 활용하지 않아야 합니다.</li>
              <li>이용자는 서비스를 정상적인 용도로만 사용해야 하며, 서비스의 안정적 운영을 방해하는 행위를 하지 않아야 합니다.</li>
              <li>이용자는 타인의 개인정보를 침해하거나 서비스를 불법적으로 이용하지 않아야 합니다.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제5조 (데이터 출처)</h2>
            <p>서비스에서 제공하는 약물 및 건강기능식품 정보의 출처는 다음과 같습니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>식품의약품안전처 의약품안전나라 (의약품 정보)</li>
              <li>식품의약품안전처 건강기능식품 정보 (건강기능식품 정보)</li>
              <li>공공데이터포털 (공공 API)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제6조 (광고)</h2>
            <p>서비스는 Google AdSense 등의 광고 서비스를 통해 운영되며, 광고와 관련하여 다음 사항이 적용됩니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>광고 콘텐츠는 서비스 제공자의 의견과 무관합니다.</li>
              <li>광고를 통한 외부 사이트 이용 시 발생하는 문제에 대해 서비스 제공자는 책임을 지지 않습니다.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제7조 (지적재산권)</h2>
            <p>서비스의 디자인, 로고, UI 구성 등에 대한 지적재산권은 서비스 제공자에게 있습니다. 공공데이터 기반의 약물 정보는 각 데이터 제공 기관의 이용 조건에 따릅니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제8조 (서비스 변경 및 중단)</h2>
            <p>서비스 제공자는 운영상, 기술상의 필요에 따라 서비스의 전부 또는 일부를 변경하거나 중단할 수 있으며, 이 경우 사전에 공지합니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제9조 (약관의 변경)</h2>
            <p>본 약관이 변경되는 경우, 변경 사항을 서비스 내 공지사항을 통해 안내하며, 변경된 약관은 공지 후 7일이 경과한 시점부터 효력이 발생합니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">제10조 (분쟁 해결)</h2>
            <p>서비스 이용과 관련하여 분쟁이 발생한 경우, 서비스 제공자의 소재지를 관할하는 법원을 전속 관할 법원으로 합니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">운영 정보</h2>
            <ul className="space-y-1">
              <li><strong>서비스명:</strong> 약잘알 (PillRight)</li>
              <li><strong>운영자:</strong> 약잘알 Team</li>
              <li><strong>문의:</strong> <a href="mailto:support@pillright.com" className="text-[var(--color-primary)] hover:underline">support@pillright.com</a></li>
              <li><strong>웹사이트:</strong> <a href="https://pillright.com" className="text-[var(--color-primary)] hover:underline">https://pillright.com</a></li>
            </ul>
          </section>
        </div>

        <AdBanner slot="legal-bottom" format="auto" className="mt-8" />
      </article>
    </>
  );
}
