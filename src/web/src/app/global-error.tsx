"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html lang="ko">
      <head>
        <style>{`
          @media (prefers-color-scheme: dark) {
            body { background-color: #0F172A !important; }
            .ge-title { color: #93C5FD !important; }
            .ge-desc { color: #9CA3AF !important; }
            .ge-btn { background-color: #2563EB !important; }
            .ge-code { color: #6B7280 !important; }
          }
        `}</style>
      </head>
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", backgroundColor: "#F8FAFC" }}>
        <div style={{ maxWidth: 480, margin: "0 auto", padding: "96px 16px", textAlign: "center" }}>
          <div className="ge-title" style={{ fontSize: 48, fontWeight: 700, color: "#1B3A5C", marginBottom: 16 }}>
            오류 발생
          </div>
          <p className="ge-desc" style={{ color: "#6B7280", marginBottom: 32 }}>
            예기치 않은 오류가 발생했습니다.
            <br />
            페이지를 새로고침하거나 잠시 후 다시 시도해주세요.
          </p>
          <button
            className="ge-btn"
            onClick={reset}
            style={{
              padding: "12px 24px",
              borderRadius: 12,
              border: "none",
              backgroundColor: "#1B3A5C",
              color: "white",
              fontWeight: 600,
              fontSize: 14,
              cursor: "pointer",
            }}
          >
            다시 시도
          </button>
          <p className="ge-code" style={{ color: "#9CA3AF", fontSize: 12, marginTop: 24 }}>
            문제가 지속되면 관리자에게 문의해주세요.
          </p>
        </div>
      </body>
    </html>
  );
}
