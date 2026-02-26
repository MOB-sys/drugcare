"use client";

import { useState } from "react";
import { SeverityBadge } from "./SeverityBadge";
import { SEVERITY_CONFIG, type Severity } from "@/lib/constants/severity";
import type { InteractionResult } from "@/types/interaction";

interface InteractionCardProps {
  interaction: InteractionResult;
}

export function InteractionCard({ interaction }: InteractionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const config = SEVERITY_CONFIG[interaction.severity as Severity] ?? SEVERITY_CONFIG.info;

  return (
    <div className={`rounded-lg border p-4 ${config.cardClassName}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left flex items-start justify-between gap-3"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <SeverityBadge severity={interaction.severity as Severity} />
            <span className="font-semibold text-gray-900 text-sm">
              {interaction.item_a_name} + {interaction.item_b_name}
            </span>
          </div>
          {interaction.description && (
            <p className="text-sm text-gray-700 line-clamp-2">{interaction.description}</p>
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
        <div className="mt-3 pt-3 border-t border-gray-200 space-y-3 text-sm">
          {interaction.mechanism && (
            <div>
              <p className="font-medium text-gray-700">작용 기전</p>
              <p className="text-gray-600">{interaction.mechanism}</p>
            </div>
          )}
          {interaction.recommendation && (
            <div>
              <p className="font-medium text-gray-700">권장 사항</p>
              <p className="text-gray-600">{interaction.recommendation}</p>
            </div>
          )}
          {interaction.ai_explanation && (
            <div>
              <p className="font-medium text-gray-700">AI 설명</p>
              <p className="text-gray-600">{interaction.ai_explanation}</p>
            </div>
          )}
          {interaction.ai_recommendation && (
            <div>
              <p className="font-medium text-gray-700">AI 권장 사항</p>
              <p className="text-gray-600">{interaction.ai_recommendation}</p>
            </div>
          )}
          <p className="text-xs text-gray-400">출처: {interaction.source}</p>
        </div>
      )}
    </div>
  );
}
