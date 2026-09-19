import type { Message } from "../types";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-card">
          <div className="empty-state-mark" aria-hidden="true">
            ◈
          </div>
          <h2>和 Qwen 开始工作</h2>
          <p>从一个问题开始，也可以让它帮你整理、分析和生成内容。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="messages-scroll" aria-live="polite">
      {[...messages]
        .sort((left, right) => left.sequence - right.sequence)
        .map((message) => (
          <article
            className={`message-row message-row--${message.role}`}
            key={message.id}
          >
            {message.role === "assistant" && <div className="message-avatar">◈</div>}
            <div className="message-content">
              <div className="message-bubble">{message.content}</div>
              <div className="message-meta">{message.role === "user" ? "你" : "Qwen"}</div>
            </div>
          </article>
        ))}
    </div>
  );
}
