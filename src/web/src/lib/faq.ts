/** Builds FAQ items from drug data fields. Shared between server (JSON-LD) and client (accordion). */

export interface FAQItem {
  question: string;
  answer: string;
}

export interface FAQSourceFields {
  drugName: string;
  efcyQesitm: string | null;
  seQesitm: string | null;
  atpnQesitm: string | null;
  intrcQesitm: string | null;
  depositMethodQesitm: string | null;
}

function truncate(text: string, maxLen = 200): string {
  if (text.length <= maxLen) return text;
  const cutoff = text.lastIndexOf(" ", maxLen - 3);
  const end = cutoff > maxLen * 0.5 ? cutoff : maxLen - 3;
  return text.slice(0, end).trimEnd() + "...";
}

export function buildDrugFAQItems(fields: FAQSourceFields): FAQItem[] {
  const { drugName, efcyQesitm, seQesitm, atpnQesitm, intrcQesitm, depositMethodQesitm } = fields;
  const items: FAQItem[] = [];

  if (efcyQesitm) {
    items.push({
      question: "이 약은 어떤 효능이 있나요?",
      answer: truncate(efcyQesitm),
    });
  }
  if (seQesitm) {
    items.push({
      question: `${drugName} 부작용은 무엇인가요?`,
      answer: truncate(seQesitm),
    });
  }
  if (atpnQesitm) {
    items.push({
      question: `${drugName} 복용 시 주의사항은?`,
      answer: truncate(atpnQesitm),
    });
  }
  if (intrcQesitm) {
    items.push({
      question: `${drugName}과 함께 먹으면 안 되는 약은?`,
      answer: truncate(intrcQesitm),
    });
  }
  if (depositMethodQesitm) {
    items.push({
      question: `${drugName} 보관방법은?`,
      answer: truncate(depositMethodQesitm),
    });
  }

  items.push({
    question: `${drugName} 복용 중 음주해도 되나요?`,
    answer:
      "약 복용 중에는 음주를 삼가는 것이 좋습니다. 알코올은 약물의 효과를 변화시키거나 부작용을 증가시킬 수 있습니다. 반드시 의사 또는 약사와 상담하세요.",
  });

  return items;
}

/** Returns FAQPage JSON-LD object for SEO structured data. */
export function buildFAQJsonLd(fields: FAQSourceFields) {
  const items = buildDrugFAQItems(fields);
  if (items.length === 0) return null;

  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}
