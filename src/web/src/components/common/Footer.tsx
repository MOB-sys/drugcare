import Link from "next/link";
import { PillRightLogo } from "./PillRightLogo";
export function Footer() {

  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-10 mt-auto">
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid gap-8 sm:grid-cols-3">
          {/* Brand */}
          <div>
            <PillRightLogo size="sm" className="mb-3" />
            <p className="text-xs text-gray-400 leading-relaxed">
              약과 영양제 상호작용을
              <br />
              3초 만에 확인하세요.
            </p>
          </div>

          {/* Quick links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">서비스</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li>
                <Link href="/check" className="hover:text-[var(--color-primary)] transition-colors">
                  상호작용 체크
                </Link>
              </li>
              <li>
                <Link href="/drugs" className="hover:text-[var(--color-primary)] transition-colors">
                  의약품 목록
                </Link>
              </li>
              <li>
                <Link href="/supplements" className="hover:text-[var(--color-primary)] transition-colors">
                  건강기능식품 목록
                </Link>
              </li>
              <li>
                <Link href="/tips" className="hover:text-[var(--color-primary)] transition-colors">
                  건강팁
                </Link>
              </li>
              <li>
                <Link href="/compare" className="hover:text-[var(--color-primary)] transition-colors">
                  약물 비교
                </Link>
              </li>
              <li>
                <Link href="/cabinet" className="hover:text-[var(--color-primary)] transition-colors">
                  내 복약함
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal + Support */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">안내</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li>
                <Link href="/privacy" className="hover:text-[var(--color-primary)] transition-colors">
                  개인정보처리방침
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-[var(--color-primary)] transition-colors">
                  이용약관
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-[var(--color-primary)] transition-colors">
                  문의하기
                </Link>
              </li>
            </ul>
            <h3 className="text-sm font-semibold text-gray-700 mt-5 mb-3">앱 다운로드</h3>
            <p className="text-sm text-gray-400">출시 예정</p>
          </div>
        </div>

        {/* Disclaimer + Copyright */}
        <div className="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-400 space-y-2">
          <p>
            약잘알은 의학적 진단이나 치료를 제공하지 않습니다.
            <br />
            제공되는 정보는 참고용이며, 반드시 의사 또는 약사와 상담하세요.
          </p>
          <p>&copy; {new Date().getFullYear()} 약잘알 (PillRight). All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
