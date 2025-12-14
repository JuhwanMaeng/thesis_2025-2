import { useParams, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { NPCTabs } from '@/components/layout/NPCTabs';
import { ToolsPanel } from '@/components/tools/ToolsPanel';
import { useState } from 'react';

export function NPCView() {
  const { npcId } = useParams<{ npcId: string }>();
  const navigate = useNavigate();
  const [showToolsPanel, setShowToolsPanel] = useState(false);

  if (!npcId) {
    return <Navigate to="/" replace />;
  }

  const handleToolsToggle = () => {
    setShowToolsPanel(!showToolsPanel);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header
        onToolsToggle={handleToolsToggle}
        showTools={showToolsPanel}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeNpcId={npcId}
          onNpcSelect={(id) => {
            // NPC 선택 시 기본 섹션(conversation)으로 이동
            navigate(`/npc/${id}/conversation`);
          }}
          onCreateNpc={() => {
            navigate('/');
          }}
          onNpcDelete={(id) => {
            if (npcId === id) {
              navigate('/');
            }
          }}
        />

        <div className="flex-1 flex flex-col overflow-hidden">
          <NPCTabs />
          <div className="flex-1 flex overflow-hidden">
            <div className="flex-1 overflow-hidden">
              <Outlet />
            </div>
            {showToolsPanel && <ToolsPanel />}
          </div>
        </div>
      </div>
    </div>
  );
}
