import { getApiHealth } from "@/lib/api/fastapi";

type LearnPageProps = {
  params: Promise<{ kcId: string }>;
};

export default async function LearnPage({ params }: LearnPageProps) {
  const { kcId } = await params;
  const health = await getApiHealth();

  return (
    <main className="page-shell">
      <section className="panel" aria-labelledby="page-title">
        <p className="eyebrow">AI Tutor</p>
        <h1 id="page-title">学習ページ</h1>
        <dl className="details">
          <div>
            <dt>学習対象</dt>
            <dd>{kcId}</dd>
          </div>
          <div>
            <dt>FastAPI</dt>
            <dd>
              <span
                className={
                  health.available ? "status status-ok" : "status status-error"
                }
              >
                {health.available ? "接続済み" : "接続できません"}
              </span>
            </dd>
          </div>
        </dl>
        {!health.available && (
          <p className="notice" role="status">
            {health.message} FastAPIが起動しているか確認してください。
          </p>
        )}
      </section>
    </main>
  );
}
