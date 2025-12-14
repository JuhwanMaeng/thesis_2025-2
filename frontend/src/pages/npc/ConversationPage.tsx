import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { ConversationPanel } from '@/components/conversation/ConversationPanel';
import { useQuery } from '@tanstack/react-query';
import { npcApi } from '@/services/api';
import type { InferenceTrace, NPC } from '@/types';

export function ConversationPage() {
  const { npcId } = useParams<{ npcId: string }>();
  const [latestTrace, setLatestTrace] = useState<InferenceTrace | null>(null);

  const { data: npc } = useQuery<NPC>({
    queryKey: ['npc', npcId],
    queryFn: () => npcApi.get(npcId!),
    enabled: !!npcId,
  });

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <ConversationPanel
        npcId={npcId}
        npcName={npc?.name}
        onTraceGenerated={setLatestTrace}
        onExpandedChange={() => {}}
        isFullPage={true}
      />
    </div>
  );
}
