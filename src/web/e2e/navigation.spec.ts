import { test, expect } from "@playwright/test";

test.describe("페이지 내비게이션", () => {
  test("홈페이지가 정상 로드된다", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/약잘알/);
    await expect(page.locator("text=상호작용 확인하기")).toBeVisible();
  });

  test("헤더 네비게이션이 동작한다", async ({ page }) => {
    await page.goto("/");

    // 상호작용 체크 링크
    await page.click("header >> text=상호작용 체크");
    await expect(page).toHaveURL(/\/check/);

    // 의약품 링크
    await page.click("header >> text=의약품");
    await expect(page).toHaveURL(/\/drugs/);

    // 건강팁 링크
    await page.click("header >> text=건강팁");
    await expect(page).toHaveURL(/\/tips/);
  });

  test("404 페이지가 정상 표시된다", async ({ page }) => {
    await page.goto("/nonexistent-page-12345");
    await expect(page.locator("text=페이지를 찾을 수 없습니다")).toBeVisible();
    await expect(page.locator("text=홈으로 가기")).toBeVisible();
  });

  test("법적 페이지가 정상 로드된다", async ({ page }) => {
    await page.goto("/privacy");
    await expect(page.locator("h1")).toContainText("개인정보처리방침");

    await page.goto("/terms");
    await expect(page.locator("h1")).toContainText("이용약관");

    await page.goto("/contact");
    await expect(page.locator("h1")).toContainText("문의하기");
  });
});
