import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NPCDashboard } from '@/components/dashboard/NPCDashboard';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { npcApi } from '@/services/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChevronDown, ChevronUp } from 'lucide-react';

import type { NPCConfig, NPC } from '@/types';

const Dashboard = () => {
  const navigate = useNavigate();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [npcName, setNpcName] = useState('');
  const [npcRole, setNpcRole] = useState('');
  const [personaId, setPersonaId] = useState('');
  const [worldId, setWorldId] = useState('');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [useLLMGeneration, setUseLLMGeneration] = useState(false);
  const [npcDescription, setNpcDescription] = useState('');
  const [initialState, setInitialState] = useState<Record<string, any>>({});
  const [npcConfig, setNpcConfig] = useState<Partial<import('@/types').NPCConfig>>({});
  const queryClient = useQueryClient();

  const { data: allNpcs = [] } = useQuery<NPC[]>({
    queryKey: ['npcs'],
    queryFn: () => npcApi.list(),
  });

  const createNpcMutation = useMutation({
    mutationFn: npcApi.create,
    onSuccess: (npc) => {
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
      setShowCreateDialog(false);
      handleResetCreateForm();
      navigate(`/npc/${npc.npc_id}/conversation`);
    },
  });

  const generateNpcMutation = useMutation({
    mutationFn: (data: { description: string; role?: string; config?: Partial<NPCConfig> }) =>
      npcApi.generate(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
      setShowCreateDialog(false);
      handleResetCreateForm();
      // NPC 생성 후 conversation 페이지로 이동
      navigate(`/npc/${result.npc.npc_id}/conversation`);
    },
  });

  const deleteNpcMutation = useMutation({
    mutationFn: (npcId: string) => npcApi.delete(npcId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['npcs'] });
    },
  });

  const handleCreateNpc = () => {
    if (useLLMGeneration) {
      if (!npcDescription.trim()) {
        alert('Please provide a description for NPC generation');
        return;
      }
      generateNpcMutation.mutate({
        description: npcDescription,
        role: npcRole || undefined,
        config: Object.keys(npcConfig).length > 0 ? npcConfig as NPCConfig : undefined,
      });
    } else {
      if (!npcName || !npcRole || !personaId || !worldId) {
        alert('Please fill in all required fields');
        return;
      }
      createNpcMutation.mutate({
        name: npcName,
        role: npcRole,
        persona_id: personaId,
        world_id: worldId,
        current_state: initialState,
        config: Object.keys(npcConfig).length > 0 ? npcConfig : undefined,
      });
    }
  };

  const handleResetCreateForm = () => {
    setNpcName('');
    setNpcRole('');
    setPersonaId('');
    setWorldId('');
    setNpcDescription('');
    setUseLLMGeneration(false);
    setInitialState({});
    setNpcConfig({});
    setShowAdvancedSettings(false);
  };

  return (
    <div className="h-full w-full flex overflow-hidden">
      <NPCDashboard
        onNpcSelect={(npcId) => {
          navigate(`/npc/${npcId}/conversation`);
        }}
        onCreateNpc={() => setShowCreateDialog(true)}
      />

      <Dialog 
        open={showCreateDialog} 
        onOpenChange={(open) => {
          setShowCreateDialog(open);
          if (!open) handleResetCreateForm();
        }}
      >
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New NPC</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex items-center gap-2 p-3 rounded-lg border border-border bg-secondary/50">
              <input
                type="checkbox"
                id="use-llm"
                checked={useLLMGeneration}
                onChange={(e) => setUseLLMGeneration(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="use-llm" className="cursor-pointer">
                Use AI to generate NPC (LLM will create persona and world automatically)
              </Label>
            </div>

            {useLLMGeneration ? (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="description">NPC Description *</Label>
                  <Textarea
                    id="description"
                    value={npcDescription}
                    onChange={(e) => setNpcDescription(e.target.value)}
                    placeholder="e.g., A wise old wizard who protects a magical forest and speaks in riddles..."
                    rows={4}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Describe the NPC you want to create. The AI will generate persona, world, and initial state.
                  </p>
                </div>
                <div>
                  <Label htmlFor="role-llm">Role (Optional)</Label>
                  <Input
                    id="role-llm"
                    value={npcRole}
                    onChange={(e) => setNpcRole(e.target.value)}
                    placeholder="Wizard, Knight, Merchant..."
                  />
                </div>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      value={npcName}
                      onChange={(e) => setNpcName(e.target.value)}
                      placeholder="NPC name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="role">Role *</Label>
                    <Input
                      id="role"
                      value={npcRole}
                      onChange={(e) => setNpcRole(e.target.value)}
                      placeholder="NPC role"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="persona">Persona ID *</Label>
                    <Input
                      id="persona"
                      value={personaId}
                      onChange={(e) => setPersonaId(e.target.value)}
                      placeholder="persona_001"
                    />
                  </div>
                  <div>
                    <Label htmlFor="world">World ID *</Label>
                    <Input
                      id="world"
                      value={worldId}
                      onChange={(e) => setWorldId(e.target.value)}
                      placeholder="world_001"
                    />
                  </div>
                </div>
              </>
            )}

            <Separator />

            <div>
              <button
                onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
                className="w-full flex items-center justify-between text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <span>Advanced Settings</span>
                {showAdvancedSettings ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
              {showAdvancedSettings && (
                <div className="mt-4 space-y-4 pl-4 border-l-2 border-border">
                  <div>
                    <Label className="text-xs font-medium text-muted-foreground uppercase">Initial State</Label>
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      <div>
                        <Label htmlFor="init-emotion" className="text-xs">Emotion</Label>
                        <Input
                          id="init-emotion"
                          value={initialState.emotion || ''}
                          onChange={(e) =>
                            setInitialState({ ...initialState, emotion: e.target.value || undefined })
                          }
                          placeholder="calm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="init-location" className="text-xs">Location</Label>
                        <Input
                          id="init-location"
                          value={initialState.location || ''}
                          onChange={(e) =>
                            setInitialState({ ...initialState, location: e.target.value || undefined })
                          }
                          placeholder="shire"
                        />
                      </div>
                      <div>
                        <Label htmlFor="init-goal" className="text-xs">Goal</Label>
                        <Input
                          id="init-goal"
                          value={initialState.goal || ''}
                          onChange={(e) =>
                            setInitialState({ ...initialState, goal: e.target.value || undefined })
                          }
                          placeholder="protect_the_ring"
                        />
                      </div>
                      <div>
                        <Label htmlFor="init-hp" className="text-xs">HP</Label>
                        <Input
                          id="init-hp"
                          type="number"
                          value={initialState.hp || ''}
                          onChange={(e) =>
                            setInitialState({
                              ...initialState,
                              hp: e.target.value ? parseInt(e.target.value) : undefined,
                            })
                          }
                          placeholder="100"
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <Label className="text-xs font-medium text-muted-foreground uppercase">NPC Configuration</Label>
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      <div>
                        <Label htmlFor="config-retrieval" className="text-xs">
                          Retrieval Top K
                        </Label>
                        <Input
                          id="config-retrieval"
                          type="number"
                          min="1"
                          max="20"
                          value={npcConfig.retrieval_top_k || ''}
                          onChange={(e) =>
                            setNpcConfig({
                              ...npcConfig,
                              retrieval_top_k: e.target.value ? parseInt(e.target.value) : undefined,
                            })
                          }
                          placeholder="5"
                        />
                      </div>
                      <div>
                        <Label htmlFor="config-importance" className="text-xs">
                          Importance Threshold
                        </Label>
                        <Input
                          id="config-importance"
                          type="number"
                          min="0"
                          max="1"
                          step="0.1"
                          value={npcConfig.importance_threshold || ''}
                          onChange={(e) =>
                            setNpcConfig({
                              ...npcConfig,
                              importance_threshold: e.target.value ? parseFloat(e.target.value) : undefined,
                            })
                          }
                          placeholder="0.7"
                        />
                      </div>
                      <div>
                        <Label htmlFor="config-reflection" className="text-xs">
                          Reflection Threshold
                        </Label>
                        <Input
                          id="config-reflection"
                          type="number"
                          min="0"
                          max="1"
                          step="0.1"
                          value={npcConfig.reflection_threshold || ''}
                          onChange={(e) =>
                            setNpcConfig({
                              ...npcConfig,
                              reflection_threshold: e.target.value ? parseFloat(e.target.value) : undefined,
                            })
                          }
                          placeholder="0.7"
                        />
                      </div>
                      <div>
                        <Label htmlFor="config-max-facts" className="text-xs">
                          Max Facts/Dimension
                        </Label>
                        <Input
                          id="config-max-facts"
                          type="number"
                          min="1"
                          max="10"
                          value={npcConfig.max_facts_per_dimension || ''}
                          onChange={(e) =>
                            setNpcConfig({
                              ...npcConfig,
                              max_facts_per_dimension: e.target.value ? parseInt(e.target.value) : undefined,
                            })
                          }
                          placeholder="3"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={() => setShowCreateDialog(false)}
                disabled={createNpcMutation.isPending || generateNpcMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                onClick={handleCreateNpc}
                disabled={
                  (useLLMGeneration
                    ? generateNpcMutation.isPending || !npcDescription.trim()
                    : createNpcMutation.isPending || !npcName || !npcRole || !personaId || !worldId)
                }
              >
                {useLLMGeneration
                  ? generateNpcMutation.isPending
                    ? 'Generating...'
                    : 'Generate NPC'
                  : createNpcMutation.isPending
                  ? 'Creating...'
                  : 'Create NPC'}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;
