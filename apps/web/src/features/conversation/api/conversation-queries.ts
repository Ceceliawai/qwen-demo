import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createConversation,
  getConversation,
  listConversations,
  sendMessage,
} from "../../../services/conversation-api";

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

  return useMutation({
    mutationFn: (content: string) => sendMessage(conversationId, content),
    onSuccess: (conversation) => {
      queryClient.setQueryData(conversationKeys.detail(conversation.id), conversation);
      queryClient.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}
