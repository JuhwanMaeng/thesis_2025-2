import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import { npcApi, memoryApi, traceApi, vectorApi, worldApi } from '@/services/api';
import { Users, Database, Brain, TrendingUp, Plus, Globe } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { NPCCard } from './NPCCard';
import type { NPC, WorldKnowledge } from '@/types';

interface NPCDashboardProps {
  onNpcSelect: (npcId: string) => void;
  onCreateNpc: () => void;
}

export function NPCDashboard({ onNpcSelect, onCreateNpc }: NPCDashboardProps) {
  const navigate = useNavigate();
  const { data: npcs = [], isLoading: npcsLoading } = useQuery<NPC[]>({
    queryKey: ['npcs'],
    queryFn: () => npcApi.list(),
  });

  const { data: worlds = [] } = useQuery<WorldKnowledge[]>({
    queryKey: ['worlds'],
    queryFn: () => worldApi.list(),
  });

  // 월드별로 NPC 그룹화
  const npcsByWorld = useMemo(() => {
    const grouped: Record<string, { world: WorldKnowledge | null; npcs: NPC[] }> = {};
    
    // 월드 정보를 맵으로 변환
    const worldMap = new Map(worlds.map(w => [w.world_id, w]));
    
    // NPC를 월드별로 그룹화
    npcs.forEach(npc => {
      const worldId = npc.world_id;
      if (!grouped[worldId]) {
        grouped[worldId] = {
          world: worldMap.get(worldId) || null,
          npcs: []
        };
      }
      grouped[worldId].npcs.push(npc);
    });
    
    // 월드가 있지만 NPC가 없는 경우도 포함
    worlds.forEach(world => {
      if (!grouped[world.world_id]) {
        grouped[world.world_id] = {
          world,
          npcs: []
        };
      }
    });
    
    return grouped;
  }, [npcs, worlds]);

  // 전체 통계를 위한 쿼리들
  const { data: allMemoriesData } = useQuery({
    queryKey: ['all-memories-stats'],
    queryFn: async () => {
      const stats = await Promise.all(
        npcs.map(async (npc) => {
          try {
            const memories = await memoryApi.getAll(npc.npc_id, 1000);
            return memories;
          } catch {
            return [];
          }
        })
      );
      const allMemories = stats.flat();
      const shortTerm = allMemories.filter((m) => m.memory_type === 'short_term').length;
      const longTerm = allMemories.filter((m) => m.memory_type === 'long_term').length;
      return { total: allMemories.length, shortTerm, longTerm };
    },
    enabled: npcs.length > 0,
  });

  const { data: allTracesData } = useQuery({
    queryKey: ['all-traces-stats'],
    queryFn: async () => {
      const counts = await Promise.all(
        npcs.map(async (npc) => {
          try {
            const traces = await traceApi.getByNpc(npc.npc_id, 100);
            return traces.length;
          } catch {
            return 0;
          }
        })
      );
      return counts.reduce((sum, count) => sum + count, 0);
    },
    enabled: npcs.length > 0,
  });

  const { data: vectorStats } = useQuery({
    queryKey: ['vector-stats'],
    queryFn: () => vectorApi.getStats(),
    enabled: npcs.length > 0,
  });

  const totalMemories = allMemoriesData?.total || 0;
  const totalTraces = allTracesData || 0;
  const totalShortTerm = allMemoriesData?.shortTerm || 0;
  const totalLongTerm = allMemoriesData?.longTerm || 0;

  const totalVectors =
    (vectorStats?.episodic.vector_count || 0) +
    (vectorStats?.persona.vector_count || 0) +
    (vectorStats?.world.vector_count || 0);

  if (npcsLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-muted-foreground text-sm">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-background">
      <ScrollArea className="flex-1">
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">NPC Dashboard</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Overview of all NPCs and system status
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => navigate('/worlds')}
              >
                <Globe className="w-4 h-4 mr-2" />
                Manage Worlds
              </Button>
              <Button onClick={onCreateNpc}>
                <Plus className="w-4 h-4 mr-2" />
                Create NPC
              </Button>
            </div>
          </div>

          {/* 통계 카드 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total NPCs</p>
                  <p className="text-2xl font-bold mt-1">{npcs.length}</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Users className="w-6 h-6 text-primary" />
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Memories</p>
                  <p className="text-2xl font-bold mt-1">{totalMemories}</p>
                  <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                    <span>Short Term: {totalShortTerm}</span>
                    <span>•</span>
                    <span>Long Term: {totalLongTerm}</span>
                  </div>
                </div>
                <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <Database className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Traces</p>
                  <p className="text-2xl font-bold mt-1">{totalTraces}</p>
                </div>
                <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </Card>

            <Card className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Vector Indexes</p>
                  <p className="text-2xl font-bold mt-1">{totalVectors}</p>
                  {vectorStats && (
                    <div className="flex flex-col gap-1 mt-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${vectorStats.episodic.index_exists ? 'bg-green-500' : 'bg-gray-400'}`} />
                        <span className="text-xs text-muted-foreground">
                          Episodic: {vectorStats.episodic.vector_count || 0}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${vectorStats.persona.index_exists ? 'bg-green-500' : 'bg-gray-400'}`} />
                        <span className="text-xs text-muted-foreground">
                          Persona: {vectorStats.persona.vector_count || 0}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${vectorStats.world.index_exists ? 'bg-green-500' : 'bg-gray-400'}`} />
                        <span className="text-xs text-muted-foreground">
                          World: {vectorStats.world.vector_count || 0}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </Card>
          </div>

          {/* 월드별 NPC 목록 */}
          {Object.keys(npcsByWorld).length > 0 ? (
            <div className="space-y-6">
              {Object.entries(npcsByWorld)
                .sort(([a], [b]) => {
                  const worldA = npcsByWorld[a].world?.title || '';
                  const worldB = npcsByWorld[b].world?.title || '';
                  return worldA.localeCompare(worldB);
                })
                .map(([worldId, { world, npcs: worldNpcs }]) => (
                  <div key={worldId}>
                    <div className="flex items-center gap-3 mb-4">
                      <Globe className="w-5 h-5 text-muted-foreground" />
                      <div>
                        <h2 className="text-lg font-semibold">
                          {world?.title || `World: ${worldId}`}
                        </h2>
                        <p className="text-xs text-muted-foreground">
                          {worldId} • {worldNpcs.length} NPC{worldNpcs.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    {worldNpcs.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {worldNpcs.map((npc) => (
                          <NPCCard key={npc.npc_id} npc={npc} onSelect={onNpcSelect} />
                        ))}
                      </div>
                    ) : (
                      <Card className="p-6">
                        <p className="text-sm text-muted-foreground text-center">
                          No NPCs in this world
                        </p>
                      </Card>
                    )}
                  </div>
                ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <Users className="w-12 h-12 mx-auto text-muted-foreground opacity-50 mb-4" />
              <h3 className="text-lg font-semibold mb-2">No NPCs yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Create your first NPC to get started
              </p>
              <Button onClick={onCreateNpc}>
                <Plus className="w-4 h-4 mr-2" />
                Create NPC
              </Button>
            </Card>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
