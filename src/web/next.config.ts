import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  trailingSlash: false,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "nedrug.mfds.go.kr",
      },
    ],
    formats: ["image/avif", "image/webp"],
  },
  async redirects() {
    return [
      {
        source: "/:path*",
        has: [{ type: "host", value: "www.pillright.com" }],
        destination: "https://pillright.com/:path*",
        permanent: true,
      },
      {
        source: "/tip",
        destination: "/tips",
        permanent: true,
      },
    ];
  },
  async rewrites() {
    return {
      beforeFiles: [
        /* Next.js 자체 API 라우트(/api/og 등)는 rewrite 제외 */
        {
          source: "/api/og",
          destination: "/api/og",
        },
      ],
      afterFiles: [
        /* 나머지 /api/* 요청은 백엔드로 프록시 */
        {
          source: "/api/:path*",
          destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
        },
      ],
      fallback: [],
    };
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-DNS-Prefetch-Control", value: "off" },
          { key: "X-Download-Options", value: "noopen" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          {
            key: "X-Robots-Tag",
            value: "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://pagead2.googlesyndication.com https://t1.kakaocdn.net https://www.google.com https://www.gstatic.com blob:",
              "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
              "img-src 'self' data: blob: https:",
              "font-src 'self' https://cdn.jsdelivr.net data:",
              "connect-src 'self' https://www.google-analytics.com https://analytics.google.com https://pagead2.googlesyndication.com https://*.sentry.io https://www.google.com",
              "frame-src 'self' https://pagead2.googlesyndication.com https://www.google.com https://tpc.googlesyndication.com",
              "object-src 'none'",
              "base-uri 'self'",
            ].join("; "),
          },
        ],
      },
      {
        /* 정적 자산 장기 캐싱 */
        source: "/icon-:size(\\d+)",
        headers: [
          { key: "Cache-Control", value: "public, max-age=31536000, immutable" },
        ],
      },
    ];
  },
  experimental: {
    optimizeCss: true,
  },
};

export default withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,

  silent: true,
  disableLogger: true,

  sourcemaps: {
    disable: !process.env.SENTRY_AUTH_TOKEN,
    deleteSourcemapsAfterUpload: true,
  },
});
