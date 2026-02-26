export function DisclaimerBanner() {
  return (
    <div className="bg-[var(--color-primary-50)] border-b border-[var(--color-primary-100)] py-2 text-center text-xs text-[var(--color-primary)]">
      <span className="inline-flex items-center gap-1.5">
        <svg className="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        이 서비스는 의사/약사의 전문적 판단을 대체하지 않습니다. 참고 정보로만 활용하세요.
      </span>
    </div>
  );
}
