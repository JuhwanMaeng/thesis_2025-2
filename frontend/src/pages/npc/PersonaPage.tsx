import { useParams } from 'react-router-dom';
import { AgentPersonaPanel } from '@/components/agent/AgentPersonaPanel';

export function PersonaPage() {
  const { npcId } = useParams<{ npcId: string }>();

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full overflow-hidden flex">
      <AgentPersonaPanel npcId={npcId} />
    </div>
  );
}
