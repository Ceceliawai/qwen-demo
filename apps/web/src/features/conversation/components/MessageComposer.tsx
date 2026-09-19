import { useState } from "react";

interface MessageComposerProps {
  isSending: boolean;
  error: boolean;
  onSend: (content: string) => Promise<void>;
}

export function MessageComposer({ isSending, error, onSend }: MessageComposerProps) {
  const [content, setContent] = useState("");
  const [isComposing, setIsComposing] = useState(false);

  const submit = async () => {
    const normalizedContent = content.trim();
    if (!normalizedContent || isSending) return;
    setContent("");
    try {
      await onSend(normalizedContent);
    } catch {
      // The message list renders the failed assistant placeholder.
    }
  };

  return (
    <div className="composer">
      <textarea
        value={content}
        onChange={(event) => setContent(event.target.value)}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey && !isComposing) {
            event.preventDefault();
            void submit();
          }
        }}
        placeholder="输入你想聊的内容…"
        rows={2}
        aria-label="消息输入框"
      />
      <div className="composer-footer">
        <span className="composer-hint">
          {error ? "发送失败，输入内容已保留" : "Enter 发送 · Shift + Enter 换行"}
        </span>
        <button
          className="send-button"
          type="button"
          disabled={!content.trim() || isSending}
          onClick={() => void submit()}
          title={isSending ? "请等待当前回答完成" : "发送消息"}
        >
          发送 →
        </button>
      </div>
    </div>
  );
}
