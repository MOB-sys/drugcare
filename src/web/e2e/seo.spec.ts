import { test, expect } from "@playwright/test";

test.describe("SEO 검증", () => {
  test("홈페이지에 필수 메타 태그가 있다", async ({ page }) => {
    await page.goto("/");

    // title
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);

    // meta description
    const description = page.locator("meta[name='description']");
    await expect(description).toHaveAttribute("content", /.+/);

    // og:title
    const ogTitle = page.locator("meta[property='og:title']");
    await expect(ogTitle).toHaveAttribute("content", /.+/);

    // og:description
    const ogDesc = page.locator("meta[property='og:description']");
    await expect(ogDesc).toHaveAttribute("content", /.+/);

    // og:image
    const ogImage = page.locator("meta[property='og:image']");
    await expect(ogImage).toHaveAttribute("content", /.+/);
  });

  test("약물 상세 페이지에 JSON-LD 구조화 데이터가 있다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");

    const jsonLd = page.locator("script[type='application/ld+json']");
    await expect(jsonLd.first()).toBeAttached();

    const content = await jsonLd.first().textContent();
    expect(content).toBeTruthy();
    const parsed = JSON.parse(content!);
    expect(parsed["@context"]).toContain("schema.org");
  });

  test("robots 메타 태그가 존재한다", async ({ page }) => {
    await page.goto("/");
    const robots = page.locator("meta[name='robots']");
    await expect(robots).toBeAttached();
    const content = await robots.getAttribute("content");
    expect(content).toBeTruthy();
  });

  test("canonical URL이 설정되어 있다", async ({ page }) => {
    await page.goto("/");
    const canonical = page.locator("link[rel='canonical']");
    await expect(canonical).toBeAttached();
    const href = await canonical.getAttribute("href");
    expect(href).toMatch(/^https?:\/\//);
  });

  test("약물 상세 페이지에도 canonical URL이 설정된다", async ({ page }) => {
    await page.goto("/drugs/acetaminophen");
    const canonical = page.locator("link[rel='canonical']");
    await expect(canonical).toBeAttached();
    const href = await canonical.getAttribute("href");
    expect(href).toMatch(/drugs/);
  });
});
