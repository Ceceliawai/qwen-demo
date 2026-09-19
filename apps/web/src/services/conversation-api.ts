import { apiRequest, getApiUrl } from "./api-client";
import type { Conversation, ConversationSummary } from "../features/conversation/types";

interface StreamMessageHandlers {
  onDelta: (content: string) => void;
}

interface StreamDeltaEvent {
  content: string;
}

interface StreamErrorEvent {
  detail: string;
}

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

export async function streamMessage(
  conversationId: string,
  content: string,
  handlers: StreamMessageHandlers,
): Promise<Conversation> {
  const response = await fetch(getApiUrl(`/conversations/${conversationId}/messages/stream`), {
    method: "POST",
    headers: {
      Accept: "text/event-stream",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  if (!response.body) {
    throw new Error("浏览器未收到流式响应");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let completedConversation: Conversation | undefined;

  const processFrame = (frame: string) => {
    let eventName = "message";
    const dataLines: string[] = [];

    for (const line of frame.split(/\r?\n/)) {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataLines.push(line.slice(5).trimStart());
    }

    if (dataLines.length === 0) return;
    const data = JSON.parse(dataLines.join("\n")) as unknown;

    if (eventName === "delta") {
      handlers.onDelta((data as StreamDeltaEvent).content);
    } else if (eventName === "completed") {
      completedConversation = data as Conversation;
    } else if (eventName === "error") {
      throw new Error((data as StreamErrorEvent).detail || "模型生成失败");
    }
  };

  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const frames = buffer.split(/\r?\n\r?\n/);
      buffer = frames.pop() ?? "";
      frames.forEach(processFrame);
      if (done) break;
    }
    if (buffer.trim()) processFrame(buffer);
  } finally {
    reader.releaseLock();
  }

  if (!completedConversation) {
    throw new Error("流式响应意外结束");
  }
  return completedConversation;
}
