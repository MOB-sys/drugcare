import { test, expect } from "@playwright/test";

test.describe("다크모드", () => {
  test("토글 버튼으로 테마가 전환된다", async ({ page }) => {
    await page.goto("/");
    const toggleBtn = page.locator("button[aria-label*='모드로 전환']").first();
    await expect(toggleBtn).toBeVisible();

    // 현재 테마 확인
    const htmlBefore = await page.locator("html").getAttribute("class");
    const dataBefore = await page.locator("html").getAttribute("data-theme");

    await toggleBtn.click();

    // 테마 클래스 또는 data-theme이 변경됨
    const htmlAfter = await page.locator("html").getAttribute("class");
    const dataAfter = await page.locator("html").getAttribute("data-theme");
    expect(htmlAfter !== htmlBefore || dataAfter !== dataBefore).toBeTruthy();
  });

  test("테마 설정이 새로고침 후에도 유지된다", async ({ page }) => {
    await page.goto("/");
    const toggleBtn = page.locator("button[aria-label*='모드로 전환']").first();
    await toggleBtn.click();

    // 전환 후 상태 기록
    const themeAfterToggle = await page.locator("html").getAttribute("class");

    // 새로고침
    await page.reload();

    // 테마가 유지됨
    const themeAfterReload = await page.locator("html").getAttribute("class");
    expect(themeAfterReload).toBe(themeAfterToggle);
  });

  test("라이트모드에서 주요 요소가 보인다", async ({ page }) => {
    await page.goto("/");
    // 라이트모드로 설정
    await page.evaluate(() => {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    });
    await page.reload();

    await expect(page.locator("header")).toBeVisible();
    await expect(page.locator("h1").first()).toBeVisible();
    await expect(page.locator("footer")).toBeVisible();
  });

  test("다크모드에서 주요 요소가 보인다", async ({ page }) => {
    await page.goto("/");
    // 다크모드로 설정
    await page.evaluate(() => {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    });
    await page.reload();

    await expect(page.locator("header")).toBeVisible();
    await expect(page.locator("h1").first()).toBeVisible();
    await expect(page.locator("footer")).toBeVisible();
  });
});
