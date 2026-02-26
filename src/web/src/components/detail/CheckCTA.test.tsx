import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { CheckCTA } from "./CheckCTA";

afterEach(cleanup);

describe("CheckCTA", () => {
  it("renders drug CTA text", () => {
    render(<CheckCTA itemType="drug" itemId={1} itemName="타이레놀" />);
    expect(screen.getAllByText("이 약의 상호작용 확인하기").length).toBeGreaterThanOrEqual(1);
  });

  it("renders supplement CTA text", () => {
    render(<CheckCTA itemType="supplement" itemId={5} itemName="비타민D" />);
    expect(screen.getAllByText("이 영양제의 상호작용 확인하기").length).toBeGreaterThanOrEqual(1);
  });

  it("links to /check with preselect param", () => {
    render(<CheckCTA itemType="drug" itemId={1} itemName="타이레놀" />);
    const link = screen.getByRole("link");
    expect(link.getAttribute("href")).toContain("/check?preselect=drug:1:");
  });
});
