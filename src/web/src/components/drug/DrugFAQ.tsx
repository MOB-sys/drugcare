"use client";

import { useState } from "react";
import type { FAQItem } from "@/lib/faq";

function FAQAccordionItem({ item }: { item: FAQItem }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border-b border-gray-100 dark:border-gray-700 last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-3 py-4 px-1 text-left text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-[var(--color-primary)] transition-colors"
        aria-expanded={open}
      >
        <span className="flex-1">{item.question}</span>
        <svg
          className={`w-4 h-4 shrink-0 text-gray-400 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div className="pb-4 px-1 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
          {item.answer}
        </div>
      )}
    </div>
  );
}

interface DrugFAQProps {
  items: FAQItem[];
}

export function DrugFAQ({ items }: DrugFAQProps) {
  if (items.length === 0) return null;

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">
        자주 묻는 질문
      </h2>
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 px-5 shadow-sm">
        {items.map((item, idx) => (
          <FAQAccordionItem key={idx} item={item} />
        ))}
      </div>
    </section>
  );
}
