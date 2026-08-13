"use client";

import { useEffect } from "react";

type ErrorPageProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="page-shell">
      <section className="panel" role="alert">
        <p className="eyebrow">AI Tutor</p>
        <h1>学習ページを表示できませんでした</h1>
        <p>
          予期しないエラーが発生しました。時間を置いてもう一度お試しください。
        </p>
        <button className="primary-button" type="button" onClick={reset}>
          再試行
        </button>
      </section>
    </main>
  );
}
