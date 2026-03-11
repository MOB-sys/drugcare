/** 질환별 약물 주의사항 — 주요 질환/대상 목록. */

export interface ConditionItem {
  keyword: string;
  label: string;
  slug: string;
  icon: string;
  description: string;
  seoDescription: string;
}

export const CONDITIONS: ConditionItem[] = [
  {
    keyword: "간질환",
    label: "간질환",
    slug: "liver-disease",
    icon: "\uD83E\uDEC1",
    description: "간염, 간경변, 지방간 등 간 기능 이상",
    seoDescription:
      "간질환(간염, 간경변, 지방간) 환자가 복용 시 주의해야 하는 의약품 목록입니다. 간 기능 저하 시 약물 대사가 느려져 부작용 위험이 높아질 수 있으므로 반드시 확인하세요.",
  },
  {
    keyword: "신장질환",
    label: "신장질환",
    slug: "kidney-disease",
    icon: "\uD83E\uDED8",
    description: "신부전, 신증후군 등 신장 기능 이상",
    seoDescription:
      "신장질환(신부전, 신증후군) 환자가 복용 시 주의해야 하는 의약품 목록입니다. 신장 기능이 저하되면 약물 배설이 지연되어 체내 농도가 높아질 수 있습니다.",
  },
  {
    keyword: "당뇨",
    label: "당뇨",
    slug: "diabetes",
    icon: "\uD83E\uDE78",
    description: "제1형/제2형 당뇨병",
    seoDescription:
      "당뇨병 환자가 복용 시 주의해야 하는 의약품 목록입니다. 혈당에 영향을 줄 수 있는 약물을 확인하고, 저혈당이나 고혈당 위험을 예방하세요.",
  },
  {
    keyword: "고혈압",
    label: "고혈압",
    slug: "hypertension",
    icon: "\u2764\uFE0F",
    description: "혈압이 정상 범위를 초과하는 상태",
    seoDescription:
      "고혈압 환자가 복용 시 주의해야 하는 의약품 목록입니다. 혈압을 상승시키거나 항고혈압제와 상호작용할 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "심장질환",
    label: "심장질환",
    slug: "heart-disease",
    icon: "\uD83E\uDEC0",
    description: "심부전, 부정맥, 협심증 등",
    seoDescription:
      "심장질환(심부전, 부정맥, 협심증) 환자가 복용 시 주의해야 하는 의약품 목록입니다. 심장 기능에 영향을 줄 수 있는 약물을 사전에 확인하세요.",
  },
  {
    keyword: "천식",
    label: "천식",
    slug: "asthma",
    icon: "\uD83C\uDF2C\uFE0F",
    description: "기관지 과민성으로 인한 호흡기 질환",
    seoDescription:
      "천식 환자가 복용 시 주의해야 하는 의약품 목록입니다. 기관지 수축을 유발하거나 천식을 악화시킬 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "위궤양",
    label: "위궤양",
    slug: "stomach-ulcer",
    icon: "\uD83D\uDD25",
    description: "위장관 점막의 궤양성 질환",
    seoDescription:
      "위궤양 환자가 복용 시 주의해야 하는 의약품 목록입니다. 위장관 출혈이나 궤양을 악화시킬 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "임부",
    label: "임부",
    slug: "pregnancy",
    icon: "\uD83E\uDD30",
    description: "임신 중인 여성에 대한 주의사항",
    seoDescription:
      "임신 중 복용 시 주의해야 하는 의약품 목록입니다. 태아에 영향을 줄 수 있는 약물을 확인하고, 임신 중 안전한 복약을 위해 반드시 의사와 상담하세요.",
  },
  {
    keyword: "수유부",
    label: "수유부",
    slug: "breastfeeding",
    icon: "\uD83C\uDF7C",
    description: "모유 수유 중인 여성에 대한 주의사항",
    seoDescription:
      "모유 수유 중 복용 시 주의해야 하는 의약품 목록입니다. 모유를 통해 아기에게 전달될 수 있는 약물 성분을 확인하세요.",
  },
  {
    keyword: "소아",
    label: "소아",
    slug: "pediatric",
    icon: "\uD83D\uDC76",
    description: "15세 미만 어린이에 대한 주의사항",
    seoDescription:
      "소아(15세 미만)에게 투여 시 주의해야 하는 의약품 목록입니다. 어린이의 체중과 발달 상태에 따라 용량 조절이 필요한 약물을 확인하세요.",
  },
  {
    keyword: "고령자",
    label: "고령자",
    slug: "elderly",
    icon: "\uD83D\uDC74",
    description: "65세 이상 고령자에 대한 주의사항",
    seoDescription:
      "고령자(65세 이상)가 복용 시 주의해야 하는 의약품 목록입니다. 노화에 따른 대사 변화로 약물 반응이 달라질 수 있으므로 용량 조절에 유의하세요.",
  },
  {
    keyword: "녹내장",
    label: "녹내장",
    slug: "glaucoma",
    icon: "\uD83D\uDC41\uFE0F",
    description: "안압 상승으로 인한 시신경 손상",
    seoDescription:
      "녹내장 환자가 복용 시 주의해야 하는 의약품 목록입니다. 안압을 상승시킬 수 있는 약물을 확인하고 눈 건강을 보호하세요.",
  },
  {
    keyword: "전립선비대",
    label: "전립선비대",
    slug: "prostate",
    icon: "\uD83D\uDD35",
    description: "배뇨 장애를 동반하는 전립선 비대",
    seoDescription:
      "전립선비대증 환자가 복용 시 주의해야 하는 의약품 목록입니다. 배뇨 장애를 악화시킬 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "갑상선",
    label: "갑상선",
    slug: "thyroid",
    icon: "\uD83E\uDD8B",
    description: "갑상선기능항진/저하증",
    seoDescription:
      "갑상선 질환 환자가 복용 시 주의해야 하는 의약품 목록입니다. 갑상선 호르몬 수치에 영향을 줄 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "알레르기",
    label: "알레르기",
    slug: "allergy",
    icon: "\uD83E\uDD27",
    description: "약물 과민반응, 아나필락시스 등",
    seoDescription:
      "알레르기 체질인 환자가 복용 시 주의해야 하는 의약품 목록입니다. 약물 과민반응이나 아나필락시스를 유발할 수 있는 성분을 확인하세요.",
  },
  {
    keyword: "뇌전증",
    label: "뇌전증",
    slug: "epilepsy",
    icon: "\u26A1",
    description: "반복적 발작을 동반하는 신경 질환",
    seoDescription:
      "뇌전증(간질) 환자가 복용 시 주의해야 하는 의약품 목록입니다. 발작 역치를 낮추거나 항경련제와 상호작용할 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "우울증",
    label: "우울증",
    slug: "depression",
    icon: "\uD83D\uDC99",
    description: "기분장애, 항우울제 관련 주의사항",
    seoDescription:
      "우울증 환자가 복용 시 주의해야 하는 의약품 목록입니다. 항우울제와 상호작용하거나 기분 변화를 유발할 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "혈액응고",
    label: "혈액응고",
    slug: "blood-clotting",
    icon: "\uD83E\uDE78",
    description: "출혈 경향, 항응고제 복용 관련",
    seoDescription:
      "혈액응고 장애 환자나 항응고제 복용자가 주의해야 하는 의약품 목록입니다. 출혈 위험을 높이거나 항응고 효과에 영향을 줄 수 있는 약물을 확인하세요.",
  },
  {
    keyword: "골다공증",
    label: "골다공증",
    slug: "osteoporosis",
    icon: "\uD83E\uDDB4",
    description: "뼈 밀도 감소 관련 주의사항",
    seoDescription:
      "골다공증 환자가 복용 시 주의해야 하는 의약품 목록입니다. 뼈 밀도에 영향을 줄 수 있거나 골다공증 치료제와 상호작용하는 약물을 확인하세요.",
  },
  {
    keyword: "결핵",
    label: "결핵",
    slug: "tuberculosis",
    icon: "\uD83E\uDEC1",
    description: "결핵 치료제 관련 주의사항",
    seoDescription:
      "결핵 환자가 복용 시 주의해야 하는 의약품 목록입니다. 결핵 치료제와 상호작용할 수 있는 약물을 확인하세요.",
  },
];

/** slug로 질환 조회. */
export function getConditionBySlug(slug: string): ConditionItem | undefined {
  return CONDITIONS.find((c) => c.slug === slug);
}

/** 모든 질환 slug 배열 반환. */
export function getAllConditionSlugs(): string[] {
  return CONDITIONS.map((c) => c.slug);
}
