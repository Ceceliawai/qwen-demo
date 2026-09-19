import { useQuery } from "@tanstack/react-query";

import { getHealth } from "../../../services/health";

interface ConversationHeaderProps {
  title: string;
}

export function ConversationHeader({ title }: ConversationHeaderProps) {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    retry: false,
    staleTime: 30_000,
  });
  const isConnected = health.isSuccess;

  return (
    <header className="main-header">
      <div className="header-title">
        <h1>{title}</h1>
        <p>保持好奇，慢慢把想法说清楚</p>
      </div>
      <div className={`status-pill${isConnected ? "" : " status-pill--error"}`}>
        <span className="status-dot" aria-hidden="true" />
        {isConnected ? "服务已连接" : "服务未连接"}
      </div>
    </header>
  );
}
