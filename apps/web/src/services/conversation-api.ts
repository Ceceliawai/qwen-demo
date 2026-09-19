import { apiRequest } from "./api-client";
import type { Conversation, ConversationSummary } from "../features/conversation/types";

export function listConversations(): Promise<ConversationSummary[]> {
  return apiRequest<ConversationSummary[]>("/conversations");
}

export function createConversation(title = "新会话"): Promise<Conversation> {
  return apiRequest<Conversation>("/conversations", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export function getConversation(conversationId: string): Promise<Conversation> {
  return apiRequest<Conversation>(`/conversations/${conversationId}`);
}

export function sendMessage(conversationId: string, content: string): Promise<Conversation> {
  return apiRequest<Conversation>(`/conversations/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}
