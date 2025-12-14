import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { memoryApi } from '@/services/api';
import type { EpisodicMemory } from '@/types';
import { format } from 'date-fns';
import { Clock, Star, Database, Zap, FileText, Trash2 } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';

type MemoryTab = 'short_term' | 'long_term' | 'all';

interface MemoryPanelProps {
  npcId: string | null;
}

function MemoryCard({ item, onDelete }: { item: EpisodicMemory; onDelete?: (id: string) => void }) {
  const sourceColors = {
    observation: 'bg-primary/20 text-primary',
    action: 'bg-success/20 text-success',
    reflection: 'bg-warning/20 text-warning',
  };

  return (
    <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2 animate-fade-in group">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm leading-relaxed flex-1">{item.content}</p>
        {onDelete && (
          <button
            onClick={() => {
              if (confirm('Delete this memory?')) {
                onDelete(item.memory_id);
              }
            }}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-destructive/20 text-destructive shrink-0"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        )}
      </div>
      <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {format(new Date(item.created_at), 'MMM d, HH:mm')}
        </div>
        <div className="flex items-center gap-1" title={`Importance: ${(item.importance * 100).toFixed(0)}% (${item.importance >= 0.7 ? 'Long-term' : 'Short-term'})`}>
          <Star className="w-3 h-3" />
          {(item.importance * 100).toFixed(0)}%
        </div>
        <span className={cn('px-1.5 py-0.5 rounded text-xs', sourceColors[item.source])}>
          {item.source}
        </span>
        {item.tags.length > 0 && (
          <div className="flex gap-1">
            {item.tags.map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 rounded bg-muted text-xs">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function MemoryPanel({ npcId }: MemoryPanelProps) {
  const [activeTab, setActiveTab] = useState<MemoryTab>('short_term');
  const queryClient = useQueryClient();

  const { data: shortTermMemories = [], isLoading: loadingShort } = useQuery({
    queryKey: ['memories', npcId, 'short_term'],
    queryFn: () => npcId ? memoryApi.getRecent(npcId, 50, 'short_term') : [],
    enabled: !!npcId && (activeTab === 'short_term' || activeTab === 'all'),
  });

  const { data: longTermMemories = [], isLoading: loadingLong } = useQuery({
    queryKey: ['memories', npcId, 'long_term'],
    queryFn: () => npcId ? memoryApi.getRecent(npcId, 50, 'long_term') : [],
    enabled: !!npcId && (activeTab === 'long_term' || activeTab === 'all'),
  });

  const deleteMemoryMutation = useMutation({
    mutationFn: (memoryId: string) => memoryApi.delete(npcId!, memoryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories', npcId] });
    },
  });

  const deleteAllMemoriesMutation = useMutation({
    mutationFn: (memoryType?: 'short_term' | 'long_term') => memoryApi.deleteByNpc(npcId!, memoryType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories', npcId] });
    },
  });

  const filteredMemories =
    activeTab === 'all'
      ? [...shortTermMemories, ...longTermMemories].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )
      : activeTab === 'short_term'
      ? shortTermMemories
      : longTermMemories;

  const isLoading = loadingShort || loadingLong;

  if (!npcId) {
    return (
      <div className="h-full flex flex-col bg-card border-t border-border">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Memory</span>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          Select an NPC to view memories
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-card border-t border-border">
      <div className="p-2 border-b border-border">
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Memory</span>
        </div>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as MemoryTab)}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="short_term" className="flex items-center gap-1.5 text-xs">
              <Zap className="w-3 h-3" />
              Short ({shortTermMemories.length})
            </TabsTrigger>
            <TabsTrigger value="long_term" className="flex items-center gap-1.5 text-xs">
              <Database className="w-3 h-3" />
              Long ({longTermMemories.length})
            </TabsTrigger>
            <TabsTrigger value="all" className="flex items-center gap-1.5 text-xs">
              <FileText className="w-3 h-3" />
              All ({shortTermMemories.length + longTermMemories.length})
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin">
        <div className="p-3 space-y-2">
          {filteredMemories.length > 0 && (
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">
                {filteredMemories.length} memor{filteredMemories.length !== 1 ? 'ies' : 'y'}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs text-destructive hover:text-destructive"
                onClick={() => {
                  const memoryType = activeTab === 'all' ? undefined : activeTab;
                  const typeLabel = memoryType || 'all';
                  if (confirm(`Delete all ${typeLabel} memories?`)) {
                    deleteAllMemoriesMutation.mutate(memoryType);
                  }
                }}
                disabled={deleteAllMemoriesMutation.isPending}
              >
                <Trash2 className="w-3 h-3 mr-1" />
                Clear {activeTab === 'all' ? 'All' : activeTab === 'short_term' ? 'Short' : 'Long'}
              </Button>
            </div>
          )}
          {isLoading ? (
            <div className="text-center text-sm text-muted-foreground py-8">Loading...</div>
          ) : filteredMemories.length > 0 ? (
            filteredMemories.map((item) => (
              <MemoryCard
                key={item.memory_id}
                item={item}
                onDelete={(id) => deleteMemoryMutation.mutate(id)}
              />
            ))
          ) : (
            <div className="flex flex-col items-center justify-center min-h-[200px] text-muted-foreground py-8">
              <Database className="w-8 h-8 mb-2 opacity-50" />
              <span className="text-sm">No {activeTab === 'all' ? '' : activeTab} memories</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
