import type { ReactNode } from "react";

/** Markdown 텍스트를 React 요소로 안전하게 변환한다 (dangerouslySetInnerHTML 미사용). */
export function MarkdownRenderer({ content }: { content: string }) {
  const blocks = content.split("\n\n").map((block, i) => {
    const trimmed = block.trim();
    if (!trimmed) return null;

    if (trimmed.startsWith("## ")) {
      return (
        <h2 key={i} className="text-xl font-bold text-[var(--color-primary)] mt-8 mb-3">
          {renderInline(trimmed.slice(3))}
        </h2>
      );
    }
    if (trimmed.startsWith("### ")) {
      return (
        <h3 key={i} className="text-lg font-semibold text-gray-800 dark:text-gray-100 mt-6 mb-2">
          {renderInline(trimmed.slice(4))}
        </h3>
      );
    }
    if (trimmed === "---") {
      return <hr key={i} className="my-6 border-gray-200 dark:border-gray-700" />;
    }
    if (trimmed.startsWith("> ")) {
      return (
        <blockquote key={i} className="border-l-4 border-[var(--color-primary-100)] pl-4 text-sm text-gray-500 dark:text-gray-400 italic my-4">
          {renderInline(trimmed.slice(2))}
        </blockquote>
      );
    }
    // 리스트 처리
    if (trimmed.startsWith("- ")) {
      const items = trimmed.split("\n").filter((line) => line.trim().startsWith("- "));
      return (
        <ul key={i} className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-200 mb-3 ml-2">
          {items.map((item, j) => (
            <li key={j}>{renderInline(item.trim().slice(2))}</li>
          ))}
        </ul>
      );
    }
    // 테이블
    if (trimmed.includes("|") && trimmed.includes("---")) {
      return renderTable(trimmed, i);
    }
    // 일반 단락
    return (
      <p key={i} className="text-gray-700 dark:text-gray-200 leading-relaxed mb-3">
        {renderInline(trimmed)}
      </p>
    );
  });

  return <div className="prose prose-gray max-w-none">{blocks}</div>;
}

/** 인라인 마크다운 (**bold**) 처리. */
function renderInline(text: string): ReactNode {
  const parts = text.split(/\*\*(.+?)\*\*/g);
  if (parts.length === 1) return text;
  return parts.map((part, j) =>
    j % 2 === 1 ? <strong key={j}>{part}</strong> : part,
  );
}

/** 간단한 마크다운 테이블 렌더링. */
function renderTable(text: string, key: number) {
  const lines = text.split("\n").filter((l) => l.trim());
  if (lines.length < 3) return null;

  const headers = lines[0].split("|").map((c) => c.trim()).filter(Boolean);
  const rows = lines.slice(2).map((line) =>
    line.split("|").map((c) => c.trim()).filter(Boolean),
  );

  return (
    <div key={key} className="overflow-x-auto mb-4">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            {headers.map((h, i) => (
              <th key={i} className="text-left py-2 pr-4 text-gray-500 dark:text-gray-400 font-medium">
                {renderInline(h)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-gray-100 dark:border-gray-700/50">
              {row.map((cell, ci) => (
                <td key={ci} className="py-2 pr-4 text-gray-700 dark:text-gray-300">
                  {renderInline(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
