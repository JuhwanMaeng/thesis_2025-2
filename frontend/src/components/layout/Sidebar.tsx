import { cn } from '@/lib/utils';
import { Brain, MessageSquare, Database, FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { npcApi } from '@/services/api';
import type { NPC } from '@/types';

interface SidebarProps {
  activeNpcId: string | null;
  onNpcSelect: (npcId: string) => void;
  onCreateNpc: () => void;
}

const navItems = [
  { id: 'conversations', label: 'Conversations', icon: MessageSquare },
  { id: 'memory', label: 'Memory', icon: Database },
  { id: 'logs', label: 'Logs', icon: FileText },
];

export function Sidebar({ activeNpcId, onNpcSelect, onCreateNpc }: SidebarProps) {
  const { data: npcs = [], isLoading, error } = useQuery({
    queryKey: ['npcs'],
    queryFn: () => npcApi.list(),
    retry: false,
  });

  return (
    <aside className="w-60 h-full flex flex-col border-r border-border bg-sidebar">
      <div className="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-1">
        <div className="text-xs text-muted-foreground mb-2 px-1 uppercase tracking-wide">NPCs</div>
        {isLoading ? (
          <div className="text-sm text-muted-foreground px-3 py-2">Loading...</div>
        ) : error ? (
          <div className="text-sm text-muted-foreground px-3 py-2">Backend not available</div>
        ) : npcs.length === 0 ? (
          <div className="text-sm text-muted-foreground px-3 py-2">No NPCs yet</div>
        ) : (
          npcs.map((npc) => (
            <button
              key={npc.npc_id}
              onClick={() => onNpcSelect(npc.npc_id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors text-left',
                activeNpcId === npc.npc_id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent'
              )}
            >
              <Brain className="w-4 h-4 shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{npc.name}</div>
                <div className="text-xs opacity-70 truncate">{npc.role}</div>
              </div>
            </button>
          ))
        )}
      </div>

      <div className="p-3 border-t border-border">
        <Button onClick={onCreateNpc} className="w-full" size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Create NPC
        </Button>
      </div>
    </aside>
  );
}
