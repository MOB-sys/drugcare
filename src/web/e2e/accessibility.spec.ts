import { test, expect } from "@playwright/test";

test.describe("접근성", () => {
  test("skip-to-content 링크가 존재한다", async ({ page }) => {
    await page.goto("/");
    const skipLink = page.locator("a[href='#main-content']");
    await expect(skipLink).toBeAttached();
  });

  test("main-content ID가 존재한다", async ({ page }) => {
    await page.goto("/");
    const main = page.locator("#main-content");
    await expect(main).toBeVisible();
  });

  test("Tab 키로 skip link에 포커스할 수 있다", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("Tab");
    const skipLink = page.locator("a[href='#main-content']");
    await expect(skipLink).toBeFocused();
  });

  test("다크모드 토글 버튼이 접근 가능하다", async ({ page }) => {
    await page.goto("/");
    const toggleBtn = page.locator("button[aria-label*='모드로 전환']").first();
    await expect(toggleBtn).toBeVisible();
  });

  test("헤더에 네비게이션 role이 있다", async ({ page }) => {
    await page.goto("/");
    const nav = page.locator("header nav");
    await expect(nav).toBeVisible();
  });
});
