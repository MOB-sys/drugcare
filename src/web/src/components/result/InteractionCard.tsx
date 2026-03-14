"use client";

import { useState } from "react";
import { SeverityBadge } from "./SeverityBadge";
import { ActionGuidanceBox } from "./ActionGuidanceBox";
import { SEVERITY_CONFIG, type Severity } from "@/lib/constants/severity";
import { FlaskIcon, CheckCircleIcon, LightbulbIcon, BoltIcon } from "@/components/icons";
import type { InteractionResult } from "@/types/interaction";

/** 심각도별 아이콘 — 색상 외 시각적 구분 (접근성). */
const SEVERITY_ICONS: Record<Severity, React.ReactNode> = {
  danger: (
    <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  ),
  warning: (
    <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  caution: (
    <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  info: (
    <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

interface InteractionCardProps {
  interaction: InteractionResult;
}

export function InteractionCard({ interaction }: InteractionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const sev: Severity = (interaction.severity in SEVERITY_CONFIG) ? interaction.severity as Severity : "info";
  const config = SEVERITY_CONFIG[sev];
  const isDanger = sev === "danger";

  return (
    <div
      data-interaction-card
      className={`rounded-xl border border-l-4 ${config.borderColor} p-4 shadow-sm ${config.cardClassName} ${isDanger ? "ring-1 ring-red-300" : ""}`}
      role="region"
      aria-label={`${config.label}: ${interaction.item_a_name} + ${interaction.item_b_name}`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        className="w-full text-left flex items-start justify-between gap-3"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`${config.iconColor}`} aria-hidden="true">{SEVERITY_ICONS[sev]}</span>
            <SeverityBadge severity={sev} />
            <span className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
              {interaction.item_a_name} + {interaction.item_b_name}
            </span>
          </div>
          {interaction.description && (
            <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 break-keep">{interaction.description}</p>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 dark:text-gray-500 shrink-0 transition-transform ${expanded ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-200/60 dark:border-gray-700/60 space-y-3 text-sm">
          {interaction.mechanism && (
            <div className="flex gap-2">
              <FlaskIcon className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">작용 기전</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.mechanism}</p>
              </div>
            </div>
          )}
          {interaction.recommendation && (
            <div className="flex gap-2">
              <CheckCircleIcon className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">권장 사항</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.recommendation}</p>
              </div>
            </div>
          )}
          {interaction.ai_explanation && (
            <div className="flex gap-2">
              <LightbulbIcon className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">AI 설명</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.ai_explanation}</p>
              </div>
            </div>
          )}
          {interaction.ai_recommendation && (
            <div className="flex gap-2">
              <BoltIcon className="w-4 h-4 text-gray-400 dark:text-gray-500 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">AI 권장 사항</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.ai_recommendation}</p>
              </div>
            </div>
          )}
          {interaction.source && (
            <p className="text-xs text-gray-400 dark:text-gray-500">출처: {interaction.source}</p>
          )}

          <ActionGuidanceBox severity={sev} />
        </div>
      )}
    </div>
  );
}
