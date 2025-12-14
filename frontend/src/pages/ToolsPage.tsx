import { ToolsPanel } from '@/components/tools/ToolsPanel';
import { useOutletContext } from 'react-router-dom';

export function ToolsPage() {
  const { showToolsPanel } = useOutletContext<{ showToolsPanel: boolean }>();

  return (
    <div className="h-full w-full overflow-hidden">
      {showToolsPanel && <ToolsPanel className="w-full h-full" />}
    </div>
  );
}
