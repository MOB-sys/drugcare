import Link from "next/link";
import { PillRightLogo } from "./PillRightLogo";

const SERVICE_LINKS = [
  { href: "/check", label: "상호작용 체크" },
  { href: "/symptoms", label: "증상검색" },
  { href: "/cabinet", label: "내 복약함" },
];

const TOOL_LINKS = [
  { href: "/drugs", label: "의약품 목록" },
  { href: "/supplements", label: "건강기능식품 목록" },
  { href: "/foods", label: "식품 목록" },
  { href: "/herbal-medicines", label: "한약재 목록" },
  { href: "/drugs/side-effects", label: "부작용 역검색" },
  { href: "/drugs/conditions", label: "질환별 주의사항" },
  { href: "/drugs/identify", label: "약 식별" },
  { href: "/compare", label: "약물 비교" },
];

const INFO_LINKS = [
  { href: "/privacy", label: "개인정보처리방침" },
  { href: "/terms", label: "이용약관" },
  { href: "/contact", label: "문의하기" },
  { href: "/tips", label: "건강팁" },
  { href: "/news", label: "소식" },
];

const DATA_SOURCES = [
  "식품의약품안전처 공공데이터",
  "DUR (의약품안전사용서비스)",
  "건강기능식품 정보",
];

function FooterLinkColumn({ title, links }: { title: string; links: { href: string; label: string }[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        {title}
      </h3>
      <ul className="space-y-2 text-sm text-gray-500 dark:text-gray-400">
        {links.map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className="hover:text-[var(--color-primary)] transition-colors"
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-10 mt-auto">
      <div className="max-w-5xl mx-auto px-4">
        {/* Top: Brand + 3-column links */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <PillRightLogo size="sm" className="mb-3" />
            <p className="text-xs text-gray-400 dark:text-gray-500 leading-relaxed">
              약과 영양제 상호작용을
              <br />
              3초 만에 확인하세요.
            </p>
          </div>

          <FooterLinkColumn title="서비스" links={SERVICE_LINKS} />
          <FooterLinkColumn title="의약품 도구" links={TOOL_LINKS} />
          <FooterLinkColumn title="안내" links={INFO_LINKS} />
        </div>

        {/* Bottom section */}
        <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800 text-center space-y-4">
          {/* Data source badges */}
          <div className="flex flex-wrap justify-center gap-2">
            {DATA_SOURCES.map((source) => (
              <span
                key={source}
                className="inline-block px-2.5 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
              >
                {source}
              </span>
            ))}
          </div>

          {/* Stats line */}
          <p className="text-xs text-gray-400 dark:text-gray-500">
            44,097개 의약품 · 44,551개 건강기능식품 · 366,629건 상호작용 데이터
          </p>

          {/* Disclaimer */}
          <p className="text-xs text-gray-400 dark:text-gray-500">
            약잘알은 의학적 진단이나 치료를 제공하지 않습니다.
            <br />
            제공되는 정보는 참고용이며, 반드시 의사 또는 약사와 상담하세요.
          </p>

          {/* Copyright */}
          <p className="text-xs text-gray-400 dark:text-gray-500">
            &copy; {new Date().getFullYear()} 약잘알 (PillRight). All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
