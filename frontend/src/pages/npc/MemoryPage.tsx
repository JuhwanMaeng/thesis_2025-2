import { useParams } from 'react-router-dom';
import { MemoryPanel } from '@/components/memory/MemoryPanel';

export function MemoryPage() {
  const { npcId } = useParams<{ npcId: string }>();

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full overflow-hidden">
      <MemoryPanel npcId={npcId} />
    </div>
  );
}
