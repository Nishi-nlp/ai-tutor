export default function Loading() {
  return (
    <main className="page-shell" aria-busy="true">
      <section className="panel">
        <p className="eyebrow">AI Tutor</p>
        <h1>学習ページを読み込んでいます</h1>
        <p>FastAPIの状態を確認しています。</p>
      </section>
    </main>
  );
}
