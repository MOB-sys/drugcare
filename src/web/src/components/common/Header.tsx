"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { PillRightLogo } from "./PillRightLogo";
import { useDarkMode } from "@/lib/hooks/useDarkMode";
import { ChevronDownIcon, CloseIcon, MenuIcon, SunIcon, MoonIcon } from "@/components/icons";

interface NavChild {
  href: string;
  label: string;
}

interface NavItem {
  href: string;
  label: string;
  children?: NavChild[];
}

const NAV_ITEMS: NavItem[] = [
  { href: "/check", label: "상호작용 체크" },
  {
    href: "/drugs",
    label: "의약품",
    children: [
      { href: "/drugs", label: "의약품 목록" },
      { href: "/drugs/side-effects", label: "부작용 역검색" },
      { href: "/drugs/conditions", label: "질환별 주의사항" },
      { href: "/drugs/identify", label: "약 식별" },
      { href: "/compare", label: "약물 비교" },
    ],
  },
  { href: "/supplements", label: "건강기능식품" },
  { href: "/foods", label: "식품" },
  { href: "/herbal-medicines", label: "한약재" },
  { href: "/symptoms", label: "증상검색" },
  { href: "/news", label: "소식" },
  { href: "/tips", label: "건강팁" },
  { href: "/cabinet", label: "내 복약함" },
];

export function Header() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const mobileMenuRef = useRef<HTMLDivElement>(null);
  const mobileToggleRef = useRef<HTMLButtonElement>(null);
  const { isDark, toggle } = useDarkMode();

  const [focusIndex, setFocusIndex] = useState(-1);
  const dropdownItemsRef = useRef<(HTMLAnchorElement | null)[]>([]);

  // 외부 클릭 또는 Escape 키로 드롭다운 닫기 + 키보드 내비게이션
  useEffect(() => {
    if (!dropdownOpen) { setFocusIndex(-1); return; }
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") { setDropdownOpen(false); return; }
      if (!dropdownRef.current) return;
      const items = dropdownItemsRef.current.filter(Boolean);
      if (e.key === "ArrowDown") {
        e.preventDefault();
        const next = focusIndex < items.length - 1 ? focusIndex + 1 : 0;
        setFocusIndex(next);
        items[next]?.focus();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const prev = focusIndex > 0 ? focusIndex - 1 : items.length - 1;
        setFocusIndex(prev);
        items[prev]?.focus();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [dropdownOpen, focusIndex]);

  // 모바일 메뉴 포커스 트래핑 + Escape 닫기
  const handleMobileKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") {
      setMobileOpen(false);
      mobileToggleRef.current?.focus();
      return;
    }
    if (e.key !== "Tab" || !mobileMenuRef.current) return;

    const focusable = mobileMenuRef.current.querySelectorAll<HTMLElement>(
      'a[href], button, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length === 0) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }, []);

  useEffect(() => {
    if (!mobileOpen) return;
    document.addEventListener("keydown", handleMobileKeyDown);
    // 메뉴 열릴 때 첫 항목으로 포커스
    const timer = setTimeout(() => {
      const first = mobileMenuRef.current?.querySelector<HTMLElement>("a[href], button");
      first?.focus();
    }, 50);
    return () => {
      document.removeEventListener("keydown", handleMobileKeyDown);
      clearTimeout(timer);
    };
  }, [mobileOpen, handleMobileKeyDown]);

  function isActive(href: string) {
    return pathname === href || pathname?.startsWith(href + "/");
  }

  function isGroupActive(item: NavItem) {
    if (isActive(item.href)) return true;
    if (item.children) {
      return item.children.some((c) => isActive(c.href));
    }
    return false;
  }

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--color-border)] bg-[var(--color-surface)]/80 backdrop-blur-md">
      <nav className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" aria-label="약잘알 홈">
          <PillRightLogo size="sm" />
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1 text-sm font-medium">
          {NAV_ITEMS.map((item) =>
            item.children ? (
              <div key={item.href} className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  aria-expanded={dropdownOpen}
                  aria-haspopup="true"
                  className={`px-3 py-2 rounded-lg transition-colors flex items-center gap-1 ${
                    isGroupActive(item)
                      ? "text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                      : "text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)]"
                  }`}
                >
                  {item.label}
                  <ChevronDownIcon className={`w-3.5 h-3.5 transition-transform ${dropdownOpen ? "rotate-180" : ""}`} />
                </button>
                {dropdownOpen && (
                  <div className="absolute top-full left-0 mt-1 w-44 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-lg py-1 z-50" role="menu">
                    {item.children.map((child, idx) => (
                      <Link
                        key={child.href}
                        href={child.href}
                        ref={(el) => { dropdownItemsRef.current[idx] = el; }}
                        role="menuitem"
                        tabIndex={-1}
                        onClick={() => setDropdownOpen(false)}
                        className={`block px-4 py-2.5 text-sm transition-colors ${
                          isActive(child.href)
                            ? "text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                            : "text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)]"
                        }`}
                      >
                        {child.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  isActive(item.href)
                    ? "text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                    : "text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)]"
                }`}
              >
                {item.label}
              </Link>
            ),
          )}

          {/* 다크모드 토글 */}
          <button
            onClick={toggle}
            className="ml-2 p-2.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)] transition-colors"
            aria-label={isDark ? "라이트 모드로 전환" : "다크 모드로 전환"}
          >
            {isDark ? <SunIcon className="w-4.5 h-4.5" /> : <MoonIcon className="w-4.5 h-4.5" />}
          </button>
        </div>

        {/* Mobile: dark toggle + hamburger */}
        <div className="md:hidden flex items-center gap-1">
          <button
            onClick={toggle}
            className="p-2.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
            aria-label={isDark ? "라이트 모드로 전환" : "다크 모드로 전환"}
          >
            {isDark ? <SunIcon /> : <MoonIcon />}
          </button>
          <button
            ref={mobileToggleRef}
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2.5 rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
            aria-label={mobileOpen ? "메뉴 닫기" : "메뉴 열기"}
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
      </nav>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <div
          ref={mobileMenuRef}
          role="navigation"
          aria-label="모바일 메뉴"
          className="md:hidden border-t border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2 space-y-1"
        >
          {NAV_ITEMS.map((item) =>
            item.children ? (
              <div key={item.href}>
                <span className="block px-3 py-2 text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wide">
                  {item.label}
                </span>
                {item.children.map((child) => (
                  <Link
                    key={child.href}
                    href={child.href}
                    onClick={() => setMobileOpen(false)}
                    className={`block pl-6 pr-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                      isActive(child.href)
                        ? "text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                        : "text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
                    }`}
                  >
                    {child.label}
                  </Link>
                ))}
              </div>
            ) : (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`block px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.href)
                    ? "text-[var(--color-primary)] bg-[var(--color-primary-50)]"
                    : "text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
                }`}
              >
                {item.label}
              </Link>
            ),
          )}
        </div>
      )}
    </header>
  );
}
