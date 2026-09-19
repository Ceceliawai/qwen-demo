import { useEffect, useState } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";

import { useCreateConversation, useConversations } from "../api/conversation-queries";
import { ConversationSidebar } from "./ConversationSidebar";

export function WorkspaceLayout() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const conversations = useConversations();
  const createMutation = useCreateConversation();
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem("qwen-sidebar-collapsed") === "true");

  useEffect(() => {
    localStorage.setItem("qwen-sidebar-collapsed", String(collapsed));
  }, [collapsed]);

  const createNewConversation = async () => {
    const conversation = await createMutation.mutateAsync();
    navigate(`/conversations/${conversation.id}`);
  };

  return (
    <div className="workspace">
      <ConversationSidebar
        conversations={conversations.data ?? []}
        activeConversationId={conversationId}
        collapsed={collapsed}
        isLoading={conversations.isPending}
        isCreating={createMutation.isPending}
        hasError={conversations.isError}
        onToggle={() => setCollapsed((value) => !value)}
        onCreate={() => void createNewConversation()}
        onSelect={(id) => navigate(`/conversations/${id}`)}
        onRetry={() => void conversations.refetch()}
      />
      <section className="main-panel">
        <Outlet />
      </section>
    </div>
  );
}
