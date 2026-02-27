"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="ko">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", backgroundColor: "#F8FAFC" }}>
        <div style={{ maxWidth: 480, margin: "0 auto", padding: "96px 16px", textAlign: "center" }}>
          <div style={{ fontSize: 48, fontWeight: 700, color: "#1B3A5C", marginBottom: 16 }}>
            오류 발생
          </div>
          <p style={{ color: "#6B7280", marginBottom: 32 }}>
            예기치 않은 오류가 발생했습니다.
            <br />
            페이지를 새로고침하거나 잠시 후 다시 시도해주세요.
          </p>
          <button
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
          {error.digest && (
            <p style={{ color: "#9CA3AF", fontSize: 12, marginTop: 24 }}>
              오류 코드: {error.digest}
            </p>
          )}
        </div>
      </body>
    </html>
  );
}
