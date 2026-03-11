import type { Metadata } from "next";
import { Breadcrumbs } from "@/components/common/Breadcrumbs";
import { AdBanner } from "@/components/ads/AdBanner";

export const metadata: Metadata = {
  title: "개인정보처리방침",
  description: "약잘알 개인정보처리방침. 수집하는 개인정보 항목, 이용 목적, 보유 기간 등을 안내합니다.",
  alternates: { canonical: "/privacy" },
};

export default function PrivacyPage() {
  return (
    <>
      <Breadcrumbs
        items={[
          { label: "홈", href: "/" },
          { label: "개인정보처리방침" },
        ]}
      />

      <article className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-6">개인정보처리방침</h1>
        <p className="text-sm text-[var(--color-text-muted)] mb-8">시행일: 2026년 2월 27일</p>

        <div className="prose-policy space-y-8 text-[var(--color-text)] text-sm leading-relaxed break-keep">
          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">1. 개인정보의 수집 및 이용 목적</h2>
            <p>약잘알(이하 &quot;서비스&quot;)은 다음의 목적을 위해 최소한의 개인정보를 처리합니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>복약함 관리 서비스 제공</li>
              <li>서비스 이용 통계 분석 및 품질 개선</li>
              <li>광고 서비스 제공 (Google AdSense)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">2. 수집하는 개인정보 항목</h2>
            <p>서비스는 회원가입 없이 이용 가능하며, 다음의 정보를 자동 수집합니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li><strong>기기 식별자:</strong> 디바이스 UUID (앱) 또는 세션 ID (웹)</li>
              <li><strong>서비스 이용 기록:</strong> 검색 기록, 복약함 데이터 (기기에 저장)</li>
              <li><strong>자동 수집 정보:</strong> IP 주소, 브라우저 종류, 방문 일시, 쿠키</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">3. 개인정보의 보유 및 이용 기간</h2>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li><strong>복약함 데이터:</strong> 사용자 기기(localStorage/SharedPreferences)에 저장되며, 사용자가 직접 삭제할 수 있습니다.</li>
              <li><strong>서버 저장 데이터:</strong> 기기 식별자 기반 복약함 데이터는 마지막 이용일로부터 1년간 보관 후 자동 삭제됩니다.</li>
              <li><strong>이용 통계:</strong> 비식별 처리 후 서비스 개선 목적으로 보관됩니다.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">4. 개인정보의 제3자 제공</h2>
            <p>서비스는 원칙적으로 이용자의 개인정보를 제3자에게 제공하지 않습니다. 다만 다음의 경우 예외로 합니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>법령에 의해 요구되는 경우</li>
              <li>광고 서비스 제공을 위해 Google에 비식별 정보 전달 (Google AdSense/AdMob 개인정보 처리방침에 따름)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">5. 쿠키(Cookie)의 사용</h2>
            <p>서비스는 다음 목적으로 쿠키를 사용합니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>세션 관리 및 사용자 설정 유지 (다크모드 등)</li>
              <li>서비스 이용 통계 (Google Analytics)</li>
              <li>맞춤형 광고 제공 (Google AdSense)</li>
            </ul>
            <p className="mt-2">브라우저 설정에서 쿠키 수집을 거부할 수 있으며, 이 경우 일부 기능 이용에 제한이 있을 수 있습니다.</p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">6. 개인정보의 안전성 확보 조치</h2>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>HTTPS(SSL/TLS) 암호화 통신</li>
              <li>민감 정보 기기 우선 저장 원칙</li>
              <li>서버 접근 권한 최소화</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">7. 이용자의 권리</h2>
            <p>이용자는 언제든지 다음의 권리를 행사할 수 있습니다.</p>
            <ul className="list-disc ml-5 mt-2 space-y-1">
              <li>복약함 데이터 삭제 (앱 또는 웹에서 직접 삭제)</li>
              <li>브라우저 캐시·쿠키 삭제를 통한 저장 정보 초기화</li>
              <li>개인정보 관련 문의 (아래 연락처)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">8. 개인정보보호 책임자</h2>
            <ul className="list-none mt-2 space-y-1">
              <li>이메일: <a href="mailto:support@pillright.com" className="text-[var(--color-info)] hover:underline">support@pillright.com</a></li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">9. 방침의 변경</h2>
            <p>본 개인정보처리방침이 변경되는 경우, 변경 사항을 서비스 내 공지사항을 통해 안내하며, 변경된 방침은 공지 후 7일이 경과한 시점부터 효력이 발생합니다.</p>
          </section>
        </div>

        <AdBanner slot="legal-bottom" format="auto" className="mt-8" />
      </article>
    </>
  );
}
