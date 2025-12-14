import { cn } from '@/lib/utils';
import { Brain, Plus, Trash2, Globe, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState, memo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { npcApi } from '@/services/api';
import { useLocation, useNavigate } from 'react-router-dom';
import type { NPC } from '@/types';

interface SidebarProps {
  activeNpcId: string | null;
  onNpcSelect: (npcId: string) => void;
  onCreateNpc: () => void;
  onNpcDelete?: (npcId: string) => void;
}

export const Sidebar = memo(function Sidebar({ activeNpcId, onNpcSelect, onCreateNpc, onNpcDelete }: SidebarProps) {
  const queryClient = useQueryClient();
  const location = useLocation();
  const navigate = useNavigate();
  const [hoveredNpcId, setHoveredNpcId] = useState<string | null>(null);
  
  // URL에서 현재 NPC ID 추출
  const urlNpcId = location.pathname.match(/\/npc\/([^/]+)/)?.[1] || null;
  const currentNpcId = activeNpcId || urlNpcId;
  const isHomePage = location.pathname === '/';
  const isWorldsPage = location.pathname === '/worlds';

  const { data: npcs = [], isLoading, error } = useQuery({
    queryKey: ['npcs'],
    queryFn: () => npcApi.list(),
    retry: false,
  });

  const deleteNpcMutation = useMutation({
    mutationFn: (npcId: string) => npcApi.delete(npcId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
      if (onNpcDelete) {
        onNpcDelete(activeNpcId || '');
      }
    },
  });

  return (
    <aside className="w-60 h-full flex flex-col border-r border-border bg-sidebar shrink-0">
      <div className="flex-1 overflow-y-auto scrollbar-thin p-3 space-y-1">
        <div className="mb-3 space-y-1">
          <button
            onClick={() => navigate('/')}
            className={cn(
              'w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
              isHomePage
                ? 'bg-primary text-primary-foreground'
                : 'text-sidebar-foreground hover:bg-sidebar-accent'
            )}
          >
            <Home className="w-4 h-4" />
            <span>Home</span>
          </button>
          <button
            onClick={() => navigate('/worlds')}
            className={cn(
              'w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors',
              isWorldsPage
                ? 'bg-primary text-primary-foreground'
                : 'text-sidebar-foreground hover:bg-sidebar-accent'
            )}
          >
            <Globe className="w-4 h-4" />
            <span>Worlds</span>
          </button>
        </div>
        <div className="text-xs text-muted-foreground mb-2 px-1 uppercase tracking-wide">NPCs</div>
        {isLoading ? (
          <div className="text-sm text-muted-foreground px-3 py-2">Loading...</div>
        ) : error ? (
          <div className="text-sm text-muted-foreground px-3 py-2">Backend not available</div>
        ) : npcs.length === 0 ? (
          <div className="text-sm text-muted-foreground px-3 py-2">No NPCs yet</div>
        ) : (
          npcs.map((npc) => (
            <div
              key={npc.npc_id}
              className={cn(
                'group relative w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors',
                currentNpcId === npc.npc_id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent'
              )}
              onMouseEnter={() => setHoveredNpcId(npc.npc_id)}
              onMouseLeave={() => setHoveredNpcId(null)}
            >
              <button
                onClick={() => onNpcSelect(npc.npc_id)}
                className="flex-1 flex items-center gap-3 text-left min-w-0"
              >
                <Brain className="w-4 h-4 shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{npc.name}</div>
                  <div className="text-xs opacity-70 truncate">{npc.role}</div>
                </div>
              </button>
              {hoveredNpcId === npc.npc_id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete NPC "${npc.name}"?`)) {
                      deleteNpcMutation.mutate(npc.npc_id);
                    }
                  }}
                  className="p-1 rounded hover:bg-destructive/20 text-destructive shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete NPC"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              )}
            </div>
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
});
