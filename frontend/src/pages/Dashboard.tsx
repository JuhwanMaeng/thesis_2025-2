import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { ConversationPanel } from '@/components/conversation/ConversationPanel';
import { AgentPersonaPanel } from '@/components/agent/AgentPersonaPanel';
import { MemoryPanel } from '@/components/memory/MemoryPanel';
import { ReasoningPanel } from '@/components/reasoning/ReasoningPanel';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { npcApi } from '@/services/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { cn } from '@/lib/utils';

import type { InferenceTrace } from '@/types';

const Dashboard = () => {
  const [activeNpcId, setActiveNpcId] = useState<string | null>(null);
  const [latestTrace, setLatestTrace] = useState<InferenceTrace | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [isConversationExpanded, setIsConversationExpanded] = useState(false);
  const [npcName, setNpcName] = useState('');
  const [npcRole, setNpcRole] = useState('');
  const [personaId, setPersonaId] = useState('');
  const [worldId, setWorldId] = useState('');
  const queryClient = useQueryClient();

  const createNpcMutation = useMutation({
    mutationFn: npcApi.create,
    onSuccess: (npc) => {
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
      setActiveNpcId(npc.npc_id);
      setIsConversationExpanded(false);
      setShowCreateDialog(false);
      setNpcName('');
      setNpcRole('');
      setPersonaId('');
      setWorldId('');
    },
  });

  const handleCreateNpc = () => {
    if (!npcName || !npcRole || !personaId || !worldId) {
      alert('Please fill in all fields');
      return;
    }
    createNpcMutation.mutate({
      name: npcName,
      role: npcRole,
      persona_id: personaId,
      world_id: worldId,
      current_state: {},
    });
  };

  const activeNpc = queryClient.getQueryData(['npc', activeNpcId]) as any;

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeNpcId={activeNpcId}
          onNpcSelect={(npcId) => {
            setActiveNpcId(npcId);
            setIsConversationExpanded(false);
          }}
          onCreateNpc={() => setShowCreateDialog(true)}
        />

        <div className="flex-1 flex overflow-hidden">
          {activeNpcId ? (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className={cn(
                "min-h-0 overflow-hidden border-b border-border",
                isConversationExpanded ? "flex-[2]" : "h-12 shrink-0"
              )}>
                <ConversationPanel
                  npcId={activeNpcId}
                  npcName={activeNpc?.name}
                  onTraceGenerated={setLatestTrace}
                  onExpandedChange={setIsConversationExpanded}
                />
              </div>
              
              <div className={cn(
                "flex overflow-hidden",
                isConversationExpanded ? "flex-1" : "flex-[2]"
              )}>
                <div className="flex-1 min-w-0 overflow-hidden">
                  <MemoryPanel npcId={activeNpcId} />
                </div>
                <div className="flex-1 min-w-0 overflow-hidden border-l border-border">
                  <ReasoningPanel npcId={activeNpcId} trace={latestTrace} />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-background">
              <div className="text-center space-y-2">
                <p className="text-muted-foreground text-lg font-medium">No NPC selected</p>
                <p className="text-muted-foreground text-sm">Select an NPC from the sidebar or create a new one</p>
              </div>
            </div>
          )}

          {activeNpcId && <AgentPersonaPanel npcId={activeNpcId} />}
        </div>
      </div>

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New NPC</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={npcName}
                onChange={(e) => setNpcName(e.target.value)}
                placeholder="NPC name"
              />
            </div>
            <div>
              <Label htmlFor="role">Role</Label>
              <Input
                id="role"
                value={npcRole}
                onChange={(e) => setNpcRole(e.target.value)}
                placeholder="NPC role"
              />
            </div>
            <div>
              <Label htmlFor="persona">Persona ID</Label>
              <Input
                id="persona"
                value={personaId}
                onChange={(e) => setPersonaId(e.target.value)}
                placeholder="persona_001"
              />
            </div>
            <div>
              <Label htmlFor="world">World ID</Label>
              <Input
                id="world"
                value={worldId}
                onChange={(e) => setWorldId(e.target.value)}
                placeholder="world_001"
              />
            </div>
            <Button
              onClick={handleCreateNpc}
              disabled={createNpcMutation.isPending}
              className="w-full"
            >
              {createNpcMutation.isPending ? 'Creating...' : 'Create NPC'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;
