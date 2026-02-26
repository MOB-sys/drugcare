import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { AdBanner } from "./AdBanner";

describe("AdBanner", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_ADSENSE_ID", "");
  });

  it("renders nothing when ADSENSE_ID is not set", () => {
    const { container } = render(<AdBanner slot="1234567890" />);
    expect(container.innerHTML).toBe("");
  });

  it("renders ins element when ADSENSE_ID is set", () => {
    vi.stubEnv("NEXT_PUBLIC_ADSENSE_ID", "ca-pub-1234567890");
    const { container } = render(<AdBanner slot="9876543210" />);
    const ins = container.querySelector("ins.adsbygoogle");
    expect(ins).not.toBeNull();
    expect(ins?.getAttribute("data-ad-slot")).toBe("9876543210");
    expect(ins?.getAttribute("data-ad-client")).toBe("ca-pub-1234567890");
  });

  it("applies format prop", () => {
    vi.stubEnv("NEXT_PUBLIC_ADSENSE_ID", "ca-pub-test");
    const { container } = render(
      <AdBanner slot="111" format="rectangle" />
    );
    const ins = container.querySelector("ins.adsbygoogle");
    expect(ins?.getAttribute("data-ad-format")).toBe("rectangle");
  });

  it("applies className prop", () => {
    vi.stubEnv("NEXT_PUBLIC_ADSENSE_ID", "ca-pub-test");
    const { container } = render(
      <AdBanner slot="111" className="extra-class" />
    );
    const wrapper = container.querySelector(".ad-banner");
    expect(wrapper?.classList.contains("extra-class")).toBe(true);
  });
});
