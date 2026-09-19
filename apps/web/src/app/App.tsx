import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { WorkspaceLayout } from "../features/conversation/components/WorkspaceLayout";
import { ConversationPage } from "../features/conversation/pages/ConversationPage";
import { WelcomePage } from "../features/conversation/pages/WelcomePage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 15_000,
      retry: false,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_relativeSplatPath: true,
          v7_startTransition: true,
        }}
      >
        <Routes>
          <Route element={<WorkspaceLayout />}>
            <Route index element={<WelcomePage />} />
            <Route path="conversations/:conversationId" element={<ConversationPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
