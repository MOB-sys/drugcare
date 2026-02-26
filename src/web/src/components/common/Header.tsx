import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <nav className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-[var(--color-brand)]">
          약먹어
        </Link>
        <div className="flex gap-6 text-sm font-medium text-gray-600">
          <Link href="/check" className="hover:text-[var(--color-brand)]">
            상호작용 체크
          </Link>
          <Link href="/tips" className="hover:text-[var(--color-brand)]">
            건강팁
          </Link>
          <Link href="/cabinet" className="hover:text-[var(--color-brand)]">
            내 복약함
          </Link>
        </div>
      </nav>
    </header>
  );
}
