import { test, expect } from "@playwright/test";

test.describe("복약함 페이지", () => {
  test("빈 상태에서 안내 메시지가 표시된다", async ({ page }) => {
    // localStorage 초기화
    await page.goto("/cabinet");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await expect(
      page.locator("text=/비어|없습니다|추가해|약물을 담아/")
    ).toBeVisible();
  });

  test("약물 상세에서 추가한 항목이 복약함에 표시된다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const addButton = page.locator("button", { hasText: /복약함|추가|담기/ });
    await addButton.click();

    await page.goto("/cabinet");
    // 추가된 약물이 목록에 표시됨
    await expect(page.locator("[data-testid='cabinet-item'], li, .cabinet-item").first()).toBeVisible();
  });

  test("복약함에서 항목 제거가 동작한다", async ({ page }) => {
    // 먼저 약물 추가
    await page.goto("/drugs/acetaminophen");
    const addButton = page.locator("button", { hasText: /복약함|추가|담기/ });
    await addButton.click();

    await page.goto("/cabinet");
    const removeButton = page.locator("button", { hasText: /제거|삭제|빼기/ }).first();
    await removeButton.click();

    // 제거 후 빈 상태이거나 항목이 사라짐
    await expect(
      page.locator("text=/비어|없습니다|추가해|약물을 담아/").or(
        page.locator("[data-testid='cabinet-empty']")
      )
    ).toBeVisible();
  });

  test("복약함 데이터가 새로고침 후에도 유지된다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const addButton = page.locator("button", { hasText: /복약함|추가|담기/ });
    await addButton.click();

    await page.goto("/cabinet");
    await expect(page.locator("[data-testid='cabinet-item'], li, .cabinet-item").first()).toBeVisible();

    // 페이지 새로고침
    await page.reload();

    // localStorage 기반이므로 데이터가 유지됨
    await expect(page.locator("[data-testid='cabinet-item'], li, .cabinet-item").first()).toBeVisible();
  });
});
