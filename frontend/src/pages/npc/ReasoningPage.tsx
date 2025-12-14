import { useParams } from 'react-router-dom';
import { ReasoningPanel } from '@/components/reasoning/ReasoningPanel';

export function ReasoningPage() {
  const { npcId } = useParams<{ npcId: string }>();

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full overflow-hidden">
      <ReasoningPanel npcId={npcId} />
    </div>
  );
}
