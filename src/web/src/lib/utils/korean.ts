/** 한글 초성 유틸리티 — 인덱스 페이지 공용. */

export const CHOSUNG = [
  "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ",
  "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
] as const;

export const ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export const ALL_LETTERS = [...CHOSUNG, ...ALPHA];

/** 한글 문자의 초성 인덱스 (0~13). 한글 범위 밖이면 -1. */
export function getChosungIndex(char: string): number {
  const code = char.charCodeAt(0);
  if (code < 0xAC00 || code > 0xD7A3) return -1;
  const chosungMap = [0, 1, 2, 3, 4, 5, 6, 6, 7, 7, 7, 8, 9, 9, 10, 11, 12, 13, 13];
  return chosungMap[Math.floor((code - 0xAC00) / 588)] ?? -1;
}

/** 문자의 첫 글자가 주어진 인덱스 키와 일치하는지 확인. */
export function matchesLetterKey(name: string, letter: string): boolean {
  const firstChar = name.charAt(0).toUpperCase();
  if (ALPHA.includes(letter)) return firstChar === letter;
  const ci = getChosungIndex(firstChar);
  return ci >= 0 && CHOSUNG[ci] === letter;
}

/** 문자의 인덱스 키 반환 (ㄱ~ㅎ, A~Z, #). */
export function getLetterKey(name: string): string {
  const firstChar = name.charAt(0).toUpperCase();
  const ci = getChosungIndex(firstChar);
  if (ci >= 0) return CHOSUNG[ci];
  if (/[A-Z]/.test(firstChar)) return firstChar;
  return "#";
}
