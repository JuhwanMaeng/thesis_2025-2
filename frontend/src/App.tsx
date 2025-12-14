import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MainLayout } from "./components/layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound.tsx";
import { NPCView } from "./pages/NPCView";
import { ConversationPage } from "./pages/npc/ConversationPage";
import { MemoryPage } from "./pages/npc/MemoryPage";
import { ReasoningPage } from "./pages/npc/ReasoningPage";
import { PersonaPage } from "./pages/npc/PersonaPage";
import { ToolsPage } from "./pages/ToolsPage";
import { WorldsPage } from "./pages/WorldsPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
      refetchOnReconnect: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/worlds" element={<WorldsPage />} />
          <Route path="/tools" element={<ToolsPage />} />
        </Route>
        <Route path="/npc/:npcId" element={<NPCView />}>
          <Route index element={<Navigate to="conversation" replace />} />
          <Route path="conversation" element={<ConversationPage />} />
          <Route path="memory" element={<MemoryPage />} />
          <Route path="reasoning" element={<ReasoningPage />} />
          <Route path="persona" element={<PersonaPage />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
