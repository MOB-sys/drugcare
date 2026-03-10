"use client";

import { useState } from "react";
import { SeverityBadge } from "./SeverityBadge";
import { ActionGuidanceBox } from "./ActionGuidanceBox";
import { SEVERITY_CONFIG, type Severity } from "@/lib/constants/severity";
import type { InteractionResult } from "@/types/interaction";

interface InteractionCardProps {
  interaction: InteractionResult;
}

export function InteractionCard({ interaction }: InteractionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const config = SEVERITY_CONFIG[interaction.severity as Severity] ?? SEVERITY_CONFIG.info;
  const isDanger = interaction.severity === "danger";

  return (
    <div
      data-interaction-card
      className={`rounded-xl border border-l-4 ${config.borderColor} p-4 shadow-sm ${config.cardClassName} ${isDanger ? "ring-1 ring-red-300" : ""}`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        className="w-full text-left flex items-start justify-between gap-3"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <SeverityBadge severity={interaction.severity as Severity} />
            <span className="font-semibold text-gray-900 dark:text-gray-100 text-sm">
              {interaction.item_a_name} + {interaction.item_b_name}
            </span>
          </div>
          {interaction.description && (
            <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 break-keep">{interaction.description}</p>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 shrink-0 transition-transform ${expanded ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-200/60 space-y-3 text-sm">
          {interaction.mechanism && (
            <div className="flex gap-2">
              <svg className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">작용 기전</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.mechanism}</p>
              </div>
            </div>
          )}
          {interaction.recommendation && (
            <div className="flex gap-2">
              <svg className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">권장 사항</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.recommendation}</p>
              </div>
            </div>
          )}
          {interaction.ai_explanation && (
            <div className="flex gap-2">
              <svg className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">AI 설명</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.ai_explanation}</p>
              </div>
            </div>
          )}
          {interaction.ai_recommendation && (
            <div className="flex gap-2">
              <svg className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">AI 권장 사항</p>
                <p className="text-gray-600 dark:text-gray-400">{interaction.ai_recommendation}</p>
              </div>
            </div>
          )}
          <p className="text-xs text-gray-400">출처: {interaction.source}</p>

          <ActionGuidanceBox severity={interaction.severity as Severity} />
        </div>
      )}
    </div>
  );
}
