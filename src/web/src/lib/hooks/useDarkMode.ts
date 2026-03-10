"use client";

import { useState, useEffect, useCallback } from "react";

type Theme = "light" | "dark" | "system";

const STORAGE_KEY = "pillright_theme";

export function useDarkMode() {
  const [theme, setThemeState] = useState<Theme>("light");
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
      if (stored) setThemeState(stored);
    } catch (e) { console.error("[useDarkMode] localStorage 읽기 실패:", e); }
  }, []);

  useEffect(() => {
    function applyTheme(t: Theme) {
      try {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        const dark = t === "dark" || (t === "system" && prefersDark);
        setIsDark(dark);
        document.documentElement.classList.toggle("dark", dark);
      } catch (e) { console.error("[useDarkMode] 테마 적용 실패:", e); }
    }

    applyTheme(theme);

    try {
      const mql = window.matchMedia("(prefers-color-scheme: dark)");
      function handleChange() { if (theme === "system") applyTheme("system"); }
      mql.addEventListener("change", handleChange);
      return () => mql.removeEventListener("change", handleChange);
    } catch (e) { console.error("[useDarkMode] matchMedia 리스너 등록 실패:", e); }
  }, [theme]);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
    try { localStorage.setItem(STORAGE_KEY, t); } catch (e) { console.error("[useDarkMode] localStorage 저장 실패:", e); }
  }, []);

  const toggle = useCallback(() => {
    setTheme(isDark ? "light" : "dark");
  }, [isDark, setTheme]);

  return { theme, isDark, setTheme, toggle };
}
