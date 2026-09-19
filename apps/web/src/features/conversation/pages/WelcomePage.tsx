import { useNavigate } from "react-router-dom";

import { useCreateConversation } from "../api/conversation-queries";
import { ConversationHeader } from "../components/ConversationHeader";

export function WelcomePage() {
  const navigate = useNavigate();
  const createMutation = useCreateConversation();

  const startConversation = async () => {
    const conversation = await createMutation.mutateAsync();
    navigate(`/conversations/${conversation.id}`);
  };

  return (
    <>
      <ConversationHeader title="新会话" />
      <div className="conversation-main">
        <div className="empty-state">
          <div className="empty-state-card">
            <div className="empty-state-mark" aria-hidden="true">
              ◈
            </div>
            <h2>和 Qwen 开始工作</h2>
            <p>从一个问题开始，也可以让它帮你整理、分析和生成内容。</p>
            <button className="empty-state-action" type="button" onClick={() => void startConversation()}>
              {createMutation.isPending ? "准备中…" : "开始一次新的对话"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
