import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useQuery } from '@tanstack/react-query';
import { memoryApi } from '@/services/api';
import type { EpisodicMemory } from '@/types';
import { format } from 'date-fns';
import { Clock, Star, Database, Zap, FileText } from 'lucide-react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';

type MemoryTab = 'short_term' | 'long_term' | 'all';

interface MemoryPanelProps {
  npcId: string | null;
}

function MemoryCard({ item }: { item: EpisodicMemory }) {
  const sourceColors = {
    observation: 'bg-primary/20 text-primary',
    action: 'bg-success/20 text-success',
    reflection: 'bg-warning/20 text-warning',
  };

  return (
    <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2 animate-fade-in">
      <p className="text-sm leading-relaxed">{item.content}</p>
      <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {format(new Date(item.created_at), 'MMM d, HH:mm')}
        </div>
        <div className="flex items-center gap-1">
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
          {isLoading ? (
            <div className="text-center text-sm text-muted-foreground py-8">Loading...</div>
          ) : filteredMemories.length > 0 ? (
            filteredMemories.map((item) => <MemoryCard key={item.memory_id} item={item} />)
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
