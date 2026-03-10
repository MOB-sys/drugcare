import { parseDosage, type DosageInfo } from "@/lib/utils/dosageParser";

interface DosageGuideProps {
  content: string;
  id?: string;
}

/** Icon card for a single dosage data point. */
function DosageCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700">
      <div className="w-9 h-9 rounded-lg bg-[var(--color-primary-50)] flex items-center justify-center shrink-0">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{label}</p>
        <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{value}</p>
      </div>
    </div>
  );
}

/** Pill icon SVG. */
function PillIcon() {
  return (
    <svg className="w-4.5 h-4.5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
    </svg>
  );
}

/** Clock icon SVG. */
function ClockIcon() {
  return (
    <svg className="w-4.5 h-4.5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

/** Calendar icon SVG. */
function CalendarIcon() {
  return (
    <svg className="w-4.5 h-4.5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}

/** Warning icon SVG. */
function MaxDoseIcon() {
  return (
    <svg className="w-4.5 h-4.5 text-[var(--color-warning)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  );
}

/** Users icon SVG. */
function UsersIcon() {
  return (
    <svg className="w-4.5 h-4.5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

/** Check if parsed data has any structured info worth showing. */
function hasStructuredData(info: DosageInfo): boolean {
  return !!(info.doseAmount || info.frequency || info.timing || info.maxDailyDose || info.ageBasedDosing.length > 0);
}

/** Structured dosage guide with icons, falling back to raw text. */
export function DosageGuide({ content, id }: DosageGuideProps) {
  const info = parseDosage(content);
  const hasData = hasStructuredData(info);

  return (
    <section id={id} className="py-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 scroll-mt-24">
      <h2 className="text-lg font-semibold text-[var(--color-primary)] mb-3">용법 · 용량</h2>

      {hasData && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
          {info.doseAmount && (
            <DosageCard icon={<PillIcon />} label="1회 투여량" value={info.doseAmount} />
          )}
          {info.frequency && (
            <DosageCard icon={<CalendarIcon />} label="투여 횟수" value={info.frequency} />
          )}
          {info.timing && (
            <DosageCard icon={<ClockIcon />} label="복용 시점" value={info.timing} />
          )}
          {info.maxDailyDose && (
            <DosageCard icon={<MaxDoseIcon />} label="1일 최대량" value={info.maxDailyDose} />
          )}
        </div>
      )}

      {hasData && info.ageBasedDosing.length > 0 && (
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <UsersIcon />
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">연령별 용량</p>
          </div>
          <div className="space-y-1.5">
            {info.ageBasedDosing.map((ad, i) => (
              <div key={i} className="flex gap-2 text-sm">
                <span className="font-semibold text-gray-700 dark:text-gray-300 min-w-[3rem]">{ad.ageGroup}</span>
                <span className="text-gray-600 dark:text-gray-400">{ad.dose}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Always show raw text as fallback / full detail */}
      <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line break-keep text-sm">
        {content}
      </p>
    </section>
  );
}
