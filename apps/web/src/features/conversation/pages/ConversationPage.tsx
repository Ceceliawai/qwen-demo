import { useParams } from "react-router-dom";

import { useConversation, useSendMessage } from "../api/conversation-queries";
import { ConversationHeader } from "../components/ConversationHeader";
import { MessageComposer } from "../components/MessageComposer";
import { MessageList } from "../components/MessageList";

export function ConversationPage() {
  const { conversationId } = useParams();
  const conversation = useConversation(conversationId);
  const sendMutation = useSendMessage(conversationId ?? "");

  if (!conversationId || conversation.isPending) {
    return <div className="center-state">正在打开会话…</div>;
  }

  if (conversation.isError || !conversation.data) {
    return (
      <div className="error-state">
        <strong>这个会话暂时无法打开</strong>
        <p>请确认后端服务正在运行，或从左侧重新选择一个会话。</p>
      </div>
    );
  }

  const currentConversation = conversation.data;

  return (
    <>
      <ConversationHeader title={currentConversation.title} />
      <div className="conversation-main">
        <MessageList messages={currentConversation.messages} />
        <MessageComposer
          isSending={sendMutation.isPending}
          error={sendMutation.isError}
          onSend={async (content) => {
            await sendMutation.mutateAsync(content);
          }}
        />
      </div>
    </>
  );
}
