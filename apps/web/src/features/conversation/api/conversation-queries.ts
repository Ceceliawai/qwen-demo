import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createConversation,
  getConversation,
  listConversations,
  streamMessage,
} from "../../../services/conversation-api";
import type { Conversation, Message } from "../types";

export const conversationKeys = {
  all: ["conversations"] as const,
  detail: (id: string) => ["conversation", id] as const,
};

export function useConversations() {
  return useQuery({
    queryKey: conversationKeys.all,
    queryFn: listConversations,
  });
}

export function useConversation(conversationId: string | undefined) {
  return useQuery({
    queryKey: conversationId ? conversationKeys.detail(conversationId) : ["conversation", "empty"],
    queryFn: () => getConversation(conversationId!),
    enabled: Boolean(conversationId),
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => createConversation(),
    onSuccess: (conversation) => {
      queryClient.setQueryData(conversationKeys.detail(conversation.id), conversation);
      queryClient.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();
  const detailKey = conversationKeys.detail(conversationId);

  const updatePendingAssistant = (update: (message: Message) => Message) => {
    queryClient.setQueryData<Conversation>(detailKey, (conversation) => {
      if (!conversation) return conversation;
      return {
        ...conversation,
        messages: conversation.messages.map((message) =>
          message.role === "assistant" && message.status === "pending"
            ? update(message)
            : message,
        ),
      };
    });
  };

  return useMutation({
    mutationFn: (content: string) =>
      streamMessage(conversationId, content, {
        onDelta: (delta) => {
          updatePendingAssistant((message) => ({
            ...message,
            content: message.content + delta,
          }));
        },
      }),
    onMutate: async (content) => {
      await queryClient.cancelQueries({ queryKey: detailKey });
      const now = new Date().toISOString();
      const optimisticId = `${Date.now()}-${Math.random().toString(36).slice(2)}`;

      queryClient.setQueryData<Conversation>(detailKey, (conversation) => {
        if (!conversation) return conversation;
        const nextSequence =
          (conversation.messages.at(-1)?.sequence ?? -1) + 1;
        return {
          ...conversation,
          updated_at: now,
          messages: [
            ...conversation.messages,
            {
              id: `optimistic-user-${optimisticId}`,
              conversation_id: conversationId,
              role: "user",
              content,
              sequence: nextSequence,
              status: "completed",
              created_at: now,
            },
            {
              id: `optimistic-assistant-${optimisticId}`,
              conversation_id: conversationId,
              role: "assistant",
              content: "",
              sequence: nextSequence + 1,
              status: "pending",
              created_at: now,
            },
          ],
        };
      });
    },
    onSuccess: (conversation) => {
      queryClient.setQueryData(detailKey, conversation);
      queryClient.invalidateQueries({ queryKey: conversationKeys.all });
    },
    onError: (error) => {
      updatePendingAssistant((message) => ({
        ...message,
        content: error instanceof Error ? error.message : "模型生成失败，请稍后重试",
        status: "failed",
      }));
    },
  });
}
