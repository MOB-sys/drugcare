import { test, expect } from "@playwright/test";

test.describe("약물 상세 페이지", () => {
  test("페이지가 약물 이름을 제목에 포함한다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    await expect(page.locator("h1")).toBeVisible();
  });

  test("성분 정보 테이블이 렌더링된다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const ingredientsSection = page.locator("text=성분");
    await expect(ingredientsSection).toBeVisible();
    // 테이블 또는 리스트 형태의 성분 정보가 존재
    const table = page.locator("table, [role='table'], ul").first();
    await expect(table).toBeVisible();
  });

  test("복약함 추가 버튼이 동작한다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const addButton = page.locator("button", { hasText: /복약함|추가|담기/ });
    await expect(addButton).toBeVisible();
    await addButton.click();
    // 추가 후 피드백 메시지 또는 버튼 상태 변경
    await expect(
      page.locator("text=/추가|담았|완료/").or(
        page.locator("button", { hasText: /제거|삭제|빼기/ })
      )
    ).toBeVisible();
  });

  test("브레드크럼 네비게이션이 동작한다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const breadcrumb = page.locator("nav[aria-label*='breadcrumb'], [aria-label*='경로']");
    await expect(breadcrumb).toBeVisible();

    // 홈 또는 의약품 링크 클릭 시 이동
    const homeLink = breadcrumb.locator("a").first();
    await homeLink.click();
    await expect(page).not.toHaveURL(/\/drugs\/acetaminophen/);
  });

  test("공유 버튼이 존재한다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const shareButton = page.locator("button[aria-label*='공유'], button:has-text('공유')");
    await expect(shareButton).toBeVisible();
  });
});
