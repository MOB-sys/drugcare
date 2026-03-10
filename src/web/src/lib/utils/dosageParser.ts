/** Parse Korean dosage text (use_method_qesitm) into structured info. */

export interface DosageInfo {
  doseAmount: string | null;
  frequency: string | null;
  timing: string | null;
  ageBasedDosing: AgeDose[];
  maxDailyDose: string | null;
  rawText: string;
}

export interface AgeDose {
  ageGroup: string;
  dose: string;
}

/** Extract dose amount from text (e.g. "1정", "2캡슐", "10mL"). */
function extractDoseAmount(text: string): string | null {
  const pattern = /(\d+\.?\d*)\s*(정|캡슐|포|mL|ml|mg|g|환|알|방울|스푼|티스푼)/;
  const match = text.match(pattern);
  return match ? `${match[1]}${match[2]}` : null;
}

/** Extract frequency (e.g. "1일 3회", "하루 2번"). */
function extractFrequency(text: string): string | null {
  const patterns = [
    /1일\s*(\d+)\s*회/,
    /하루\s*(\d+)\s*회/,
    /하루\s*(\d+)\s*번/,
    /(\d+)일\s*(\d+)\s*회/,
    /매\s*(\d+)\s*시간/,
  ];
  for (const p of patterns) {
    const match = text.match(p);
    if (match) return match[0];
  }
  return null;
}

/** Extract timing (e.g. "식전", "식후", "취침전"). */
function extractTiming(text: string): string | null {
  const timings = ["식후", "식전", "취침전", "식간", "공복시", "공복", "아침", "저녁", "취침시"];
  for (const t of timings) {
    if (text.includes(t)) return t;
  }
  return null;
}

/** Extract age-based dosing instructions. */
function extractAgeBasedDosing(text: string): AgeDose[] {
  const results: AgeDose[] = [];
  const patterns = [
    { regex: /성인[^.,:]*?[:\s]?\s*([^.]*?(?:정|캡슐|포|mL|ml|mg|g)[^.]*)/g, group: "성인" },
    { regex: /소아[^.,:]*?[:\s]?\s*([^.]*?(?:정|캡슐|포|mL|ml|mg|g)[^.]*)/g, group: "소아" },
    { regex: /(\d+)\s*세\s*이상[^.,:]*?[:\s]?\s*([^.]*)/g, group: "" },
    { regex: /(\d+)\s*세\s*미만[^.,:]*?[:\s]?\s*([^.]*)/g, group: "" },
    { regex: /영아[^.,:]*?[:\s]?\s*([^.]*)/g, group: "영아" },
  ];

  for (const { regex, group } of patterns) {
    let match;
    while ((match = regex.exec(text)) !== null) {
      if (group) {
        results.push({ ageGroup: group, dose: match[1].trim() });
      } else {
        const ageGroup = match[0].split(/[:\s]/)[0].trim();
        const dose = match[match.length - 1].trim();
        results.push({ ageGroup, dose });
      }
    }
  }
  return results;
}

/** Extract max daily dose. */
function extractMaxDailyDose(text: string): string | null {
  const patterns = [
    /1일\s*최대\s*([^.]*?(?:정|캡슐|포|mL|ml|mg|g)[^.]*)/,
    /최대\s*(?:1일\s*)?([^.]*?(?:정|캡슐|포|mL|ml|mg|g)[^.]*)/,
    /(?:초과|넘지)\s*않[^.]*?([^.]*?(?:정|캡슐|포|mL|ml|mg|g)[^.]*)/,
  ];
  for (const p of patterns) {
    const match = text.match(p);
    if (match) return match[1].trim();
  }
  return null;
}

/** Parse raw dosage text into structured dosage information. */
export function parseDosage(text: string | null | undefined): DosageInfo {
  if (!text) {
    return {
      doseAmount: null,
      frequency: null,
      timing: null,
      ageBasedDosing: [],
      maxDailyDose: null,
      rawText: "",
    };
  }
  return {
    doseAmount: extractDoseAmount(text),
    frequency: extractFrequency(text),
    timing: extractTiming(text),
    ageBasedDosing: extractAgeBasedDosing(text),
    maxDailyDose: extractMaxDailyDose(text),
    rawText: text,
  };
}
