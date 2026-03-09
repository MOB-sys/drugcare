/** 약 외형 식별용 색상/모양 데이터. */

export interface PillColor {
  value: string;
  label: string;
  hex: string;
}

export interface PillShape {
  value: string;
  label: string;
}

export const PILL_COLORS: PillColor[] = [
  { value: "흰색", label: "흰색", hex: "#FFFFFF" },
  { value: "노란색", label: "노란색", hex: "#FFD600" },
  { value: "연노란색", label: "연노란색", hex: "#FFF9C4" },
  { value: "주황색", label: "주황색", hex: "#FF9800" },
  { value: "분홍색", label: "분홍색", hex: "#F48FB1" },
  { value: "연분홍색", label: "연분홍색", hex: "#FCE4EC" },
  { value: "빨간색", label: "빨간색", hex: "#F44336" },
  { value: "파란색", label: "파란색", hex: "#2196F3" },
  { value: "초록색", label: "초록색", hex: "#4CAF50" },
  { value: "연두색", label: "연두색", hex: "#C6FF00" },
  { value: "갈색", label: "갈색", hex: "#795548" },
  { value: "보라색", label: "보라색", hex: "#9C27B0" },
  { value: "회색", label: "회색", hex: "#9E9E9E" },
  { value: "검은색", label: "검은색", hex: "#212121" },
];

export const PILL_SHAPES: PillShape[] = [
  { value: "원형", label: "원형" },
  { value: "타원형", label: "타원형" },
  { value: "장방형", label: "장방형" },
  { value: "캡슐", label: "캡슐" },
  { value: "삼각형", label: "삼각형" },
  { value: "사각형", label: "사각형" },
  { value: "오각형", label: "오각형" },
  { value: "마름모", label: "마름모" },
];
