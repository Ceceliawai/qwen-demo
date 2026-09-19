import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import type { Message } from "../types";
import { MessageList } from "./MessageList";

function message(overrides: Partial<Message>): Message {
  return {
    id: "message-1",
    conversation_id: "conversation-1",
    role: "assistant",
    content: "",
    sequence: 0,
    status: "pending",
    created_at: "2026-09-19T00:00:00Z",
    ...overrides,
  };
}

test("shows a thinking indicator before the first streamed token", () => {
  render(<MessageList messages={[message({})]} />);

  expect(screen.getByRole("status")).toHaveTextContent("思考中");
});

test("shows streamed content with a generation cursor", () => {
  render(<MessageList messages={[message({ content: "正在回答" })]} />);

  expect(screen.getByText("正在回答")).toBeInTheDocument();
  expect(screen.getByLabelText("正在生成")).toBeInTheDocument();
});
