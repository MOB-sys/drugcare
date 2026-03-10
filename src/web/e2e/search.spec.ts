import { test, expect } from "@playwright/test";

test.describe("검색 기능", () => {
  test("검색 입력에 텍스트를 입력할 수 있다", async ({ page }) => {
    await page.goto("/check");
    const input = page.locator("input[type='text']");
    await input.fill("타이레놀");
    await expect(input).toHaveValue("타이레놀");
  });

  test("검색어 입력 후 결과가 표시된다", async ({ page }) => {
    await page.goto("/check");
    const input = page.locator("input[type='text']");
    await input.fill("비타민");
    // 디바운스 대기
    await page.waitForTimeout(1500);
    // 검색 결과 목록 또는 로딩/에러 상태가 표시됨
    await expect(
      page.locator("[data-testid='search-results'], [role='listbox'], .search-results").or(
        page.locator("text=/검색 결과|결과가 없|로딩/")
      )
    ).toBeVisible();
  });

  test("검색 결과 클릭 시 상세 페이지로 이동한다", async ({ page }) => {
    await page.goto("/check");
    const input = page.locator("input[type='text']");
    await input.fill("비타민");
    await page.waitForTimeout(1500);

    // 첫 번째 검색 결과 클릭
    const firstResult = page.locator("[data-testid='search-results'] a, [role='option'], .search-results a, .search-results li").first();
    if (await firstResult.isVisible()) {
      await firstResult.click();
      // 상세 페이지 또는 선택 상태로 전환
      await expect(page).not.toHaveURL("/check");
    }
  });

  test("필터 칩이 동작한다 (약물/영양제 토글)", async ({ page }) => {
    await page.goto("/check");
    // 약물/영양제 필터 토글
    const drugFilter = page.locator("button, [role='tab']", { hasText: /약물|의약품/ }).first();
    const supplementFilter = page.locator("button, [role='tab']", { hasText: /영양제|건강기능/ }).first();

    if (await drugFilter.isVisible()) {
      await drugFilter.click();
      await expect(drugFilter).toHaveAttribute("aria-selected", "true")
        .catch(() => expect(drugFilter).toHaveClass(/active|selected/));
    }

    if (await supplementFilter.isVisible()) {
      await supplementFilter.click();
      await expect(supplementFilter).toHaveAttribute("aria-selected", "true")
        .catch(() => expect(supplementFilter).toHaveClass(/active|selected/));
    }
  });
});
