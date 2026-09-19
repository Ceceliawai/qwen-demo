import type { ConversationSummary } from "../types";

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | undefined;
  collapsed: boolean;
  isLoading: boolean;
  isCreating: boolean;
  hasError: boolean;
  onToggle: () => void;
  onCreate: () => void;
  onSelect: (id: string) => void;
  onRetry: () => void;
}

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return "刚刚";
  return new Intl.DateTimeFormat("zh-CN", { month: "numeric", day: "numeric" }).format(date);
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  collapsed,
  isLoading,
  isCreating,
  hasError,
  onToggle,
  onCreate,
  onSelect,
  onRetry,
}: ConversationSidebarProps) {
  return (
    <aside className={`sidebar${collapsed ? " sidebar--collapsed" : ""}`}>
      <div className="brand-row">
        <div className="brand-mark" aria-hidden="true">
          ◈
        </div>
        <div className="brand-copy">
          <strong>QWEN WORKSPACE</strong>
          <span>AI THINKING SPACE</span>
        </div>
        <button className="sidebar-toggle" type="button" onClick={onToggle} aria-label="折叠侧边栏">
          {collapsed ? "»" : "«"}
        </button>
      </div>

      <button className="new-conversation" type="button" onClick={onCreate} disabled={isCreating}>
        <strong>＋</strong>
        <span>{isCreating ? "创建中" : "新建会话"}</span>
      </button>

      <p className="sidebar-section-label">最近会话</p>
      {hasError ? (
        <div className="error-state">
          <span>暂时无法加载</span>
          {!collapsed && (
            <button className="retry-button" type="button" onClick={onRetry}>
              重试
            </button>
          )}
        </div>
      ) : isLoading ? (
        <div className="center-state">加载中…</div>
      ) : conversations.length === 0 ? (
        <div className="center-state">还没有会话</div>
      ) : (
        <ul className="conversation-list">
          {conversations.map((conversation) => (
            <li key={conversation.id}>
              <button
                className={`conversation-item${
                  activeConversationId === conversation.id ? " conversation-item--active" : ""
                }`}
                type="button"
                onClick={() => onSelect(conversation.id)}
                title={collapsed ? conversation.title : undefined}
              >
                <span className="conversation-item-icon" aria-hidden="true">
                  ◷
                </span>
                <span className="conversation-copy">
                  <span className="conversation-title">{conversation.title}</span>
                  <span className="conversation-time">{formatTime(conversation.updated_at)}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="sidebar-footer">{collapsed ? "" : "一个安静的思考空间"}</div>
    </aside>
  );
}
