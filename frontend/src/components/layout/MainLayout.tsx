import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useState, memo } from 'react';

export const MainLayout = memo(function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const isToolsPage = location.pathname === '/tools';
  const [showToolsPanel, setShowToolsPanel] = useState(true);

  const handleToolsToggle = () => {
    if (isToolsPage) {
      // Tools 페이지에서는 패널 토글
      setShowToolsPanel(!showToolsPanel);
    } else {
      // 다른 페이지에서는 Tools 페이지로 이동
      navigate('/tools');
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header
        onToolsToggle={handleToolsToggle}
        showTools={isToolsPage ? showToolsPanel : false}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeNpcId={null}
          onNpcSelect={(npcId) => navigate(`/npc/${npcId}/conversation`)}
          onCreateNpc={() => navigate('/')}
          onNpcDelete={() => {}}
        />
        <div className="flex-1 overflow-hidden min-w-0 h-full">
          <Outlet context={{ showToolsPanel, setShowToolsPanel }} />
        </div>
      </div>
    </div>
  );
});
