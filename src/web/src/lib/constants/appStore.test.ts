import { describe, it, expect, vi, afterEach } from "vitest";
import { getStoreUrl, getStoreUrlForPlatform } from "./appStore";

describe("getStoreUrl", () => {
  it("generates iOS App Store URL with UTM params", () => {
    const url = getStoreUrl("ios", "website", "footer");
    expect(url).toContain("apps.apple.com");
    expect(url).toContain("utm_source=website");
    expect(url).toContain("utm_medium=footer");
  });

  it("generates Android Play Store URL with UTM params", () => {
    const url = getStoreUrl("android", "website", "banner");
    expect(url).toContain("play.google.com");
    expect(url).toContain("com.yakmeogeo.app");
    expect(url).toContain("utm_source=website");
    expect(url).toContain("utm_medium=banner");
  });

  it("includes campaign when provided", () => {
    const url = getStoreUrl("ios", "website", "cta", "spring-2026");
    expect(url).toContain("utm_campaign=spring-2026");
  });

  it("omits campaign when not provided", () => {
    const url = getStoreUrl("android", "website", "footer");
    expect(url).not.toContain("utm_campaign");
  });
});

describe("getStoreUrlForPlatform", () => {
  const originalNavigator = globalThis.navigator;

  afterEach(() => {
    Object.defineProperty(globalThis, "navigator", {
      value: originalNavigator,
      writable: true,
    });
  });

  it("returns iOS URL for iPhone user agent", () => {
    Object.defineProperty(globalThis, "navigator", {
      value: { userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)" },
      writable: true,
    });
    const url = getStoreUrlForPlatform("test");
    expect(url).toContain("apps.apple.com");
    expect(url).toContain("utm_medium=test");
  });

  it("returns Android URL for Android user agent", () => {
    Object.defineProperty(globalThis, "navigator", {
      value: { userAgent: "Mozilla/5.0 (Linux; Android 13)" },
      writable: true,
    });
    const url = getStoreUrlForPlatform("test");
    expect(url).toContain("play.google.com");
  });

  it("returns Android URL when navigator is undefined", () => {
    Object.defineProperty(globalThis, "navigator", {
      value: undefined,
      writable: true,
    });
    const url = getStoreUrlForPlatform("fallback");
    expect(url).toContain("play.google.com");
    expect(url).toContain("utm_medium=fallback");
  });
});
