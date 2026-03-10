import { test, expect } from "@playwright/test";

test.describe("모바일 반응형", () => {
  test("모바일 뷰포트에서 햄버거 메뉴가 표시된다", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    const hamburger = page.locator(
      "button[aria-label*='메뉴'], button[aria-label*='menu'], [data-testid='mobile-menu-button']"
    );
    await expect(hamburger).toBeVisible();
  });

  test("데스크톱 뷰포트에서 전체 네비게이션이 표시된다", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/");

    const nav = page.locator("header nav");
    await expect(nav).toBeVisible();

    // 네비게이션 링크가 직접 보임
    await expect(page.locator("header >> text=상호작용 체크")).toBeVisible();
    await expect(page.locator("header >> text=의약품")).toBeVisible();
  });

  test("320px 너비에서 콘텐츠가 읽을 수 있다", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("/");

    // 수평 스크롤 없이 콘텐츠가 뷰포트 안에 있는지 확인
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(320);

    // 주요 콘텐츠가 보임
    await expect(page.locator("h1").first()).toBeVisible();
    await expect(page.locator("text=상호작용 확인하기")).toBeVisible();
  });

  test("모바일 햄버거 메뉴 클릭 시 네비게이션이 열린다", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    const hamburger = page.locator(
      "button[aria-label*='메뉴'], button[aria-label*='menu'], [data-testid='mobile-menu-button']"
    );
    await hamburger.click();

    // 메뉴 항목들이 보임
    await expect(
      page.locator("[data-testid='mobile-menu'], [role='menu'], .mobile-nav").or(
        page.locator("text=상호작용 체크")
      )
    ).toBeVisible();
  });
});
