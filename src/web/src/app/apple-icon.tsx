import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#1B3A5C",
          borderRadius: "36px",
        }}
      >
        <svg
          width="110"
          height="110"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M7.05 7.05a7 7 0 0 1 9.9 0l-9.9 9.9a7 7 0 0 1 0-9.9z"
            fill="white"
            opacity="0.9"
          />
          <path
            d="M16.95 16.95a7 7 0 0 1-9.9 0l9.9-9.9a7 7 0 0 1 0 9.9z"
            fill="white"
            opacity="0.5"
          />
        </svg>
      </div>
    ),
    { ...size },
  );
}
