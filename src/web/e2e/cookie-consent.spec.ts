import { test, expect } from "@playwright/test";

test.describe("쿠키 동의 배너", () => {
  test.beforeEach(async ({ page }) => {
    // 쿠키/localStorage 초기화하여 첫 방문 상태로 만듦
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.removeItem("cookie-consent");
      document.cookie.split(";").forEach((c) => {
        document.cookie = c.trim().split("=")[0] + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
      });
    });
  });

  test("첫 방문 시 쿠키 동의 배너가 표시된다", async ({ page }) => {
    await page.reload();
    const banner = page.locator(
      "[data-testid='cookie-consent'], [role='dialog']:has-text('쿠키'), .cookie-banner"
    ).or(page.locator("text=/쿠키.*사용|개인정보.*동의/"));
    await expect(banner).toBeVisible();
  });

  test("동의 버튼 클릭 시 배너가 사라진다", async ({ page }) => {
    await page.reload();
    const acceptButton = page.locator("button", { hasText: /동의|수락|모두 허용|Accept/ });
    await acceptButton.click();

    const banner = page.locator(
      "[data-testid='cookie-consent'], [role='dialog']:has-text('쿠키'), .cookie-banner"
    );
    await expect(banner).not.toBeVisible();
  });

  test("동의 후 새로고침해도 배너가 다시 나타나지 않는다", async ({ page }) => {
    await page.reload();
    const acceptButton = page.locator("button", { hasText: /동의|수락|모두 허용|Accept/ });
    await acceptButton.click();

    // 새로고침
    await page.reload();

    const banner = page.locator(
      "[data-testid='cookie-consent'], [role='dialog']:has-text('쿠키'), .cookie-banner"
    );
    await expect(banner).not.toBeVisible();
  });

  test("필수 쿠키만 허용 옵션이 동작한다", async ({ page }) => {
    await page.reload();
    const essentialOnly = page.locator("button", { hasText: /필수만|Essential|최소/ });

    if (await essentialOnly.isVisible()) {
      await essentialOnly.click();

      const banner = page.locator(
        "[data-testid='cookie-consent'], [role='dialog']:has-text('쿠키'), .cookie-banner"
      );
      await expect(banner).not.toBeVisible();

      // 설정이 저장됨
      const consent = await page.evaluate(() => localStorage.getItem("cookie-consent"));
      expect(consent).toBeTruthy();
    }
  });
});
