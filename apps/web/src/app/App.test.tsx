import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { App } from "./App";

afterEach(() => {
  vi.restoreAllMocks();
});

test("renders a successful backend health status", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok", service: "qwen-demo-server" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );

  expect(screen.getByRole("heading", { name: "AI 工作台正在初始化" })).toBeInTheDocument();
  expect(await screen.findByText("Backend connected")).toBeInTheDocument();
});
