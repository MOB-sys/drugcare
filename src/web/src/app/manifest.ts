import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "약잘알 (PillRight) — 약/영양제 상호작용 체커",
    short_name: "약잘알",
    description: "이 약이랑 이 영양제, 같이 먹어도 될까? 3초 만에 확인하는 복약 안전 체커.",
    start_url: "/",
    display: "standalone",
    background_color: "#F8FAFC",
    theme_color: "#1B3A5C",
    orientation: "portrait-primary",
    categories: ["health", "medical"],
    icons: [
      {
        src: "/icon-192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        src: "/icon-512.png",
        sizes: "512x512",
        type: "image/png",
      },
      {
        src: "/icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
