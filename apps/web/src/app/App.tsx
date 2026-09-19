import { useQuery } from "@tanstack/react-query";

import { getHealth } from "../services/health";

export function App() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    retry: false,
  });

  const statusLabel = health.isPending
    ? "正在检查后端连接"
    : health.isSuccess
      ? "Backend connected"
      : "Backend unavailable";

  return (
    <main className="workspace-shell">
      <section className="workspace-card" aria-labelledby="app-title">
        <p className="eyebrow">QWEN DEMO · FOUNDATION</p>
        <h1 id="app-title">AI 工作台正在初始化</h1>
        <p className="description">
          前后端工程骨架已经建立。下一步将接入项目、会话和百炼 Qwen 文本问答。
        </p>
        <div className="status-pill">
          <span className="status-dot" aria-hidden="true" />
          {statusLabel}
        </div>
      </section>
    </main>
  );
}
