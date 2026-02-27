import { ImageResponse } from "@vercel/og";
import { type NextRequest } from "next/server";

export const runtime = "edge";

const PRIMARY_COLOR = "#1B3A5C";
const PRIMARY_DARK = "#132B45";
const DRUG_BG = "#EEF2F7";
const SUPPLEMENT_BG = "#ECFDF5";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const title = searchParams.get("title") || "PillRight";
  const description = searchParams.get("description") || "";
  const type = searchParams.get("type") || "drug";

  const bgColor = type === "supplement" ? SUPPLEMENT_BG : DRUG_BG;
  const typeLabel = type === "supplement" ? "건강기능식품" : type === "tip" ? "건강팁" : "의약품";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: bgColor,
          padding: "60px",
        }}
      >
        {/* 상단 브랜드 */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "12px",
              backgroundColor: PRIMARY_COLOR,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: "24px",
              fontWeight: 700,
            }}
          >
            P
          </div>
          <span
            style={{
              fontSize: "28px",
              fontWeight: 700,
              color: PRIMARY_COLOR,
            }}
          >
            PillRight
          </span>
        </div>

        {/* 분류 태그 */}
        <div
          style={{
            display: "flex",
            padding: "6px 16px",
            borderRadius: "20px",
            backgroundColor: PRIMARY_COLOR,
            color: "white",
            fontSize: "18px",
            fontWeight: 600,
            marginBottom: "20px",
          }}
        >
          {typeLabel}
        </div>

        {/* 제목 */}
        <div
          style={{
            fontSize: "44px",
            fontWeight: 700,
            color: PRIMARY_DARK,
            textAlign: "center",
            lineHeight: 1.3,
            maxWidth: "900px",
            overflow: "hidden",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
          }}
        >
          {title}
        </div>

        {/* 설명 */}
        {description && (
          <div
            style={{
              fontSize: "22px",
              color: "#666",
              textAlign: "center",
              marginTop: "16px",
              maxWidth: "800px",
              overflow: "hidden",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
            }}
          >
            {description}
          </div>
        )}

        {/* 하단 URL */}
        <div
          style={{
            position: "absolute",
            bottom: "30px",
            fontSize: "18px",
            color: "#999",
          }}
        >
          pillright.com
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    },
  );
}
