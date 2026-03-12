/**
 * 식약처 약효분류번호(class_no) → drugCategories slug 매핑.
 * 주요 분류코드 ~40개를 커버하여 약물 상세 페이지에서
 * 분류 기반 폴백 콘텐츠를 생성할 때 사용합니다.
 */

import { getCategoryBySlug, type DrugCategory } from "./drugCategories";

/** class_no 3자리 → drugCategories slug */
const classNoToSlug: Record<string, string> = {
  // 진통소염제
  "114": "pain-relievers", // 해열·진통·소염제
  "131": "pain-relievers", // 아세틸살리실산 계
  "114a": "pain-relievers",
  "116": "pain-relievers", // 항류마티스제

  // 소화제
  "232": "digestive-medicines", // 소화성궤양용제
  "233": "digestive-medicines", // 건위소화제
  "234": "digestive-medicines", // 제산제
  "235": "digestive-medicines", // 하제·정장제
  "236": "digestive-medicines", // 이담제
  "239": "digestive-medicines", // 기타 소화기관용약

  // 항히스타민제
  "441": "antihistamines", // 항히스타민제

  // 항생제
  "611": "antibiotics", // 주로 그람양성균에 작용
  "612": "antibiotics", // 주로 그람음성균에 작용
  "613": "antibiotics", // 광범위항생물질
  "614": "antibiotics", // 항결핵제
  "615": "antibiotics", // 항진균제
  "616": "antibiotics", // 항원충제
  "617": "antibiotics", // 항바이러스제
  "619": "antibiotics", // 기타 화학요법제

  // 혈압약
  "214": "blood-pressure-medications", // 혈압강하제
  "212": "blood-pressure-medications", // 혈관확장제
  "213": "blood-pressure-medications", // 이뇨제

  // 당뇨약
  "396": "diabetes-medications", // 당뇨병용제

  // 고지혈증약
  "218": "cholesterol-medications", // 고지혈증용제

  // 수면제
  "112": "sleep-medications", // 최면·진정제
  "113": "sleep-medications", // 항불안제

  // 스테로이드
  "245": "steroids", // 부신호르몬제

  // 호흡기약
  "222": "respiratory-medications", // 진해거담제
  "223": "respiratory-medications", // 기관지확장제
  "224": "respiratory-medications", // 함수제

  // 피부약
  "265": "dermatological-medications", // 외피용약
  "266": "dermatological-medications", // 기타 외피용약

  // 안약
  "131a": "eye-medications", // 안과용제 (맵핑 fallback)
  "271": "eye-medications", // 산동·조절마비제
  "272": "eye-medications", // 녹내장치료제
  "279": "eye-medications", // 기타 안과용제
};

/**
 * 약효분류번호로 DrugCategory를 가져옵니다.
 * 3자리 코드의 접두사(앞 3자리)로도 매칭을 시도합니다.
 */
export function getCategoryForClassNo(
  classNo: string | null | undefined,
): DrugCategory | undefined {
  if (!classNo) return undefined;

  const trimmed = classNo.trim();

  // 정확한 매칭
  const slug = classNoToSlug[trimmed];
  if (slug) return getCategoryBySlug(slug);

  // 앞 3자리로 매칭 시도 (class_no가 4자리 이상인 경우)
  if (trimmed.length > 3) {
    const prefix = trimmed.slice(0, 3);
    const prefixSlug = classNoToSlug[prefix];
    if (prefixSlug) return getCategoryBySlug(prefixSlug);
  }

  return undefined;
}
