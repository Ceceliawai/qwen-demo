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

test("renders assistant content as GitHub-flavored Markdown", () => {
  render(
    <MessageList
      messages={[
        message({
          content: "## 回答\n\n- **重点**\n- ~~旧内容~~\n\n| 名称 | 状态 |\n| --- | --- |\n| API | 正常 |",
          status: "completed",
        }),
      ]}
    />,
  );

  expect(screen.getByRole("heading", { name: "回答" })).toBeInTheDocument();
  expect(screen.getByText("重点").tagName).toBe("STRONG");
  expect(screen.getByText("旧内容").tagName).toBe("DEL");
  expect(screen.getByRole("table")).toBeInTheDocument();
});
