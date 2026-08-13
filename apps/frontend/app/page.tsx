import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="panel">
        <p className="eyebrow">AI Tutor</p>
        <h1>線形結合の学習環境</h1>
        <p>Next.js App Routerの基盤を準備しました。</p>
        <Link className="primary-link" href="/learn/la.linear_combination">
          学習ページを開く
        </Link>
      </section>
    </main>
  );
}
