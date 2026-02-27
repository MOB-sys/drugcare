import { test, expect } from "@playwright/test";

test.describe("상호작용 체크 플로우", () => {
  test("체크 페이지가 정상 로드된다", async ({ page }) => {
    await page.goto("/check");
    await expect(page.locator("h1")).toContainText("상호작용 체크");
    await expect(page.locator("input[type='text']")).toBeVisible();
  });

  test("검색 입력이 동작한다", async ({ page }) => {
    await page.goto("/check");
    const input = page.locator("input[type='text']");
    await input.fill("비타민");
    // 디바운스 후 결과가 나타나기를 기다림 (API가 없으면 에러 표시)
    await page.waitForTimeout(1000);
  });

  test("약물 비교 페이지가 정상 로드된다", async ({ page }) => {
    await page.goto("/compare");
    await expect(page.locator("h1")).toContainText("약물 비교");
    await expect(page.locator("text=비교할 약물 두 개를 선택해주세요")).toBeVisible();
  });
});
