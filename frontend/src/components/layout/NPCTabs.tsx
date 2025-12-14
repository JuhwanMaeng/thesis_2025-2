import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { MessageSquare, Database, Brain, User, Wrench } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useQuery } from '@tanstack/react-query';
import { npcApi } from '@/services/api';
import type { NPC } from '@/types';

const tabs = [
  { id: 'conversation', label: 'Conversation', icon: MessageSquare, path: 'conversation' },
  { id: 'memory', label: 'Memory', icon: Database, path: 'memory' },
  { id: 'reasoning', label: 'Reasoning', icon: Brain, path: 'reasoning' },
  { id: 'persona', label: 'Persona', icon: User, path: 'persona' },
];

export function NPCTabs() {
  const { npcId } = useParams<{ npcId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const { data: npc } = useQuery<NPC>({
    queryKey: ['npc', npcId],
    queryFn: () => npcApi.get(npcId!),
    enabled: !!npcId,
  });

  // 현재 활성 탭 결정
  const currentPath = location.pathname.split('/').pop() || 'conversation';
  const activeTabId = tabs.find(tab => tab.path === currentPath)?.id || 'conversation';

  const handleTabClick = (path: string) => {
    if (npcId) {
      navigate(`/npc/${npcId}/${path}`);
    }
  };

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-12 border-b border-border bg-card shrink-0 flex items-center px-4 gap-1">
      <div className="flex items-center gap-2 mr-4 pr-4 border-r border-border">
        <span className="text-sm font-semibold">{npc?.name || 'NPC'}</span>
        <span className="text-xs text-muted-foreground">({npc?.role})</span>
      </div>
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTabId === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.path)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              isActive
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
            )}
          >
            <Icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
