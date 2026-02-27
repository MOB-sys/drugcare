import Link from "next/link";
import { MediCheckLogo } from "./MediCheckLogo";

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-10 mt-auto">
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid gap-8 sm:grid-cols-3">
          {/* Brand */}
          <div>
            <MediCheckLogo size="sm" className="mb-3" />
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

          {/* App download */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">앱 다운로드</h3>
            <div className="flex flex-col gap-2 text-sm">
              <a
                href="https://apps.apple.com/app/yakmeogeo"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-[var(--color-primary)] transition-colors"
              >
                App Store
              </a>
              <a
                href="https://play.google.com/store/apps/details?id=com.yakmeogeo.app"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-[var(--color-primary)] transition-colors"
              >
                Google Play
              </a>
            </div>
          </div>
        </div>

        {/* Disclaimer + Copyright */}
        <div className="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-400 space-y-2">
          <p>
            MediCheck는 의학적 진단이나 치료를 제공하지 않습니다.
            <br />
            제공되는 정보는 참고용이며, 반드시 의사 또는 약사와 상담하세요.
          </p>
          <p>&copy; {new Date().getFullYear()} MediCheck. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
