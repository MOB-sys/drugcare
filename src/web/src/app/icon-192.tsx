import { ImageResponse } from "next/og";

export const size = { width: 192, height: 192 };
export const contentType = "image/png";

export default function Icon192() {
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
          borderRadius: "38px",
          color: "white",
          fontSize: "96px",
          fontWeight: 700,
        }}
      >
        P
      </div>
    ),
    { ...size },
  );
}
