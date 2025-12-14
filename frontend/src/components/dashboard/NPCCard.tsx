import { useQuery } from '@tanstack/react-query';
import { memoryApi, traceApi } from '@/services/api';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import type { NPC } from '@/types';

interface NPCCardProps {
  npc: NPC;
  onSelect: (npcId: string) => void;
}

export function NPCCard({ npc, onSelect }: NPCCardProps) {
  const { data: memoryStats } = useQuery({
    queryKey: ['memory-stats', npc.npc_id],
    queryFn: async () => {
      try {
        const memories = await memoryApi.getAll(npc.npc_id, 1000);
        const shortTerm = memories.filter((m) => m.memory_type === 'short_term').length;
        const longTerm = memories.filter((m) => m.memory_type === 'long_term').length;
        return { total: memories.length, shortTerm, longTerm };
      } catch {
        return { total: 0, shortTerm: 0, longTerm: 0 };
      }
    },
  });

  const { data: traceCount } = useQuery({
    queryKey: ['trace-stats', npc.npc_id],
    queryFn: async () => {
      try {
        const traces = await traceApi.getByNpc(npc.npc_id, 100);
        return traces.length;
      } catch {
        return 0;
      }
    },
  });

  const memoryStatsData = memoryStats || { total: 0, shortTerm: 0, longTerm: 0 };
  const traceCountData = traceCount || 0;

  return (
    <Card
      className="p-4 hover:bg-secondary/50 transition-colors cursor-pointer group"
      onClick={() => onSelect(npc.npc_id)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm truncate">{npc.name}</h3>
          <p className="text-xs text-muted-foreground mt-0.5">{npc.role}</p>
        </div>
        <Badge variant="outline" className="text-xs shrink-0">
          {npc.npc_id.split('_')[1]}
        </Badge>
      </div>

      <div className="space-y-2">
        {/* 상태 정보 */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {npc.current_state.location && (
            <div className="flex items-center gap-1">
              <span>📍</span>
              <span>{npc.current_state.location}</span>
            </div>
          )}
          {npc.current_state.emotion && (
            <div className="flex items-center gap-1">
              <span>😊</span>
              <span>{npc.current_state.emotion}</span>
            </div>
          )}
        </div>

        {/* 통계 */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground">Memories</p>
            <p className="text-sm font-medium">{memoryStatsData.total}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Traces</p>
            <p className="text-sm font-medium">{traceCountData}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">LT Ratio</p>
            <p className="text-sm font-medium">
              {memoryStatsData.total > 0
                ? Math.round((memoryStatsData.longTerm / memoryStatsData.total) * 100)
                : 0}
              %
            </p>
          </div>
        </div>

        {/* Config 정보 */}
        {npc.config && (
          <div className="pt-2 border-t border-border">
            <p className="text-xs text-muted-foreground mb-1">Config</p>
            <div className="flex flex-wrap gap-1">
              <Badge variant="secondary" className="text-xs">
                K={npc.config.retrieval_top_k}
              </Badge>
              <Badge variant="secondary" className="text-xs">
                I={Math.round(npc.config.importance_threshold * 100)}%
              </Badge>
              <Badge variant="secondary" className="text-xs">
                R={Math.round(npc.config.reflection_threshold * 100)}%
              </Badge>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
