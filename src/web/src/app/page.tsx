export default function HomePage() {
  return (
    <section className="max-w-3xl mx-auto px-4 py-16 text-center">
      <h1 className="text-4xl font-bold mb-4">
        이 약이랑 이 영양제,
        <br />
        <span className="text-[var(--color-brand)]">같이 먹어도 돼?</span>
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        3초 만에 확인하는 복약 안전 체커
      </p>
      <a
        href="/check"
        className="inline-block px-8 py-3 rounded-lg text-white font-semibold bg-[var(--color-brand)] hover:bg-[var(--color-brand-dark)] transition-colors"
      >
        상호작용 확인하기
      </a>
    </section>
  );
}
