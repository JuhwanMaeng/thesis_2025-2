import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { npcApi, personaApi } from '@/services/api';
import { Edit2, Target, Sparkles, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import type { NPC, PersonaProfile, NPCConfig } from '@/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';

interface AgentPersonaPanelProps {
  npcId: string | null;
}

export function AgentPersonaPanel({ npcId }: AgentPersonaPanelProps) {
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showConfigDialog, setShowConfigDialog] = useState(false);
  const [showConfigSection, setShowConfigSection] = useState(false);
  const queryClient = useQueryClient();

  const { data: npc } = useQuery<NPC>({
    queryKey: ['npc', npcId],
    queryFn: () => npcApi.get(npcId!),
    enabled: !!npcId,
  });

  const { data: persona } = useQuery<PersonaProfile>({
    queryKey: ['persona', npc?.persona_id],
    queryFn: () => personaApi.get(npc!.persona_id),
    enabled: !!npc?.persona_id,
  });

  const updatePersonaMutation = useMutation({
    mutationFn: ({ personaId, data }: { personaId: string; data: Partial<PersonaProfile> }) =>
      personaApi.update(personaId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['persona', npc?.persona_id] });
      setShowEditDialog(false);
    },
  });

  const updateConfigMutation = useMutation({
    mutationFn: (config: NPCConfig) => npcApi.updateConfig(npcId!, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['npc', npcId] });
      setShowConfigDialog(false);
    },
  });

  if (!npcId || !npc) {
    return (
      <div className="w-full h-full flex flex-col border-r border-border bg-card overflow-hidden">
        <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          Select an NPC to view persona
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col bg-card overflow-hidden">
      <div className="p-4 border-b border-border shrink-0">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold">NPC Persona</h3>
          {persona && (
            <button
              onClick={() => setShowEditDialog(true)}
              className="p-1.5 rounded hover:bg-secondary transition-colors"
              title="Edit Persona"
            >
              <Edit2 className="w-3.5 h-3.5 text-muted-foreground" />
            </button>
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h4 className="font-medium">{npc.name}</h4>
            <span className="text-xs text-muted-foreground">{npc.role}</span>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1 min-w-0">
        <div className="p-4 space-y-5 min-w-0">
          <div>
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Current State
            </label>
            <div className="mt-2 space-y-1.5">
              {npc.current_state.emotion && (
                <div className="text-sm break-words">
                  <span className="text-muted-foreground">Emotion: </span>
                  <span className="break-words">{npc.current_state.emotion}</span>
                </div>
              )}
              {npc.current_state.goal && (
                <div className="text-sm break-words">
                  <span className="text-muted-foreground">Goal: </span>
                  <span className="break-words">{npc.current_state.goal}</span>
                </div>
              )}
              {npc.current_state.location && (
                <div className="text-sm break-words">
                  <span className="text-muted-foreground">Location: </span>
                  <span className="break-words">{npc.current_state.location}</span>
                </div>
              )}
            </div>
          </div>

          {persona && (
            <>
              {persona.traits.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-3.5 h-3.5 text-muted-foreground" />
                    <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Traits
                    </label>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {persona.traits.map((trait) => (
                      <span
                        key={trait}
                        className="px-2.5 py-1 rounded-md bg-secondary text-xs font-medium break-words"
                      >
                        {trait}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {persona.goals.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-3.5 h-3.5 text-muted-foreground" />
                    <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Goals
                    </label>
                  </div>
                  <ul className="space-y-1.5">
                    {persona.goals.map((goal) => (
                      <li key={goal} className="flex items-start gap-2 text-sm break-words">
                        <span className="w-1.5 h-1.5 rounded-full bg-success mt-2 shrink-0" />
                        <span className="break-words">{goal}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {persona.habits.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-3.5 h-3.5 text-muted-foreground" />
                    <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Habits
                    </label>
                  </div>
                  <ul className="space-y-1.5">
                    {persona.habits.map((habit) => (
                      <li key={habit} className="flex items-start gap-2 text-sm break-words">
                        <span className="w-1.5 h-1.5 rounded-full bg-info mt-2 shrink-0" />
                        <span className="break-words">{habit}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {persona.background && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Background
                  </label>
                  <p className="mt-2 text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap break-words">
                    {persona.background}
                  </p>
                </div>
              )}

              {persona.speech_style && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    Speech Style
                  </label>
                  <p className="mt-2 text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap break-words">
                    {persona.speech_style}
                  </p>
                </div>
              )}
            </>
          )}

          <Separator />

          {/* NPC Configuration */}
          <div>
            <button
              onClick={() => setShowConfigSection(!showConfigSection)}
              className="w-full flex items-center justify-between text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 hover:text-foreground transition-colors"
            >
              <div className="flex items-center gap-2">
                <Settings className="w-3.5 h-3.5" />
                NPC Configuration
              </div>
              {showConfigSection ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
            {showConfigSection && (
              <div className="mt-2 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Retrieval Top K:</span>
                  <span className="font-mono">{npc.config?.retrieval_top_k ?? 5}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Importance Threshold:</span>
                  <span className="font-mono">{(npc.config?.importance_threshold ?? 0.7) * 100}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Reflection Threshold:</span>
                  <span className="font-mono">{(npc.config?.reflection_threshold ?? 0.7) * 100}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Facts/Dimension:</span>
                  <span className="font-mono">{npc.config?.max_facts_per_dimension ?? 3}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-2"
                  onClick={() => setShowConfigDialog(true)}
                >
                  <Settings className="w-3 h-3 mr-2" />
                  Edit Configuration
                </Button>
              </div>
            )}
          </div>
        </div>
      </ScrollArea>

      {persona && (
        <PersonaEditDialog
          persona={persona}
          open={showEditDialog}
          onOpenChange={setShowEditDialog}
          onSave={(data) => {
            if (persona.persona_id) {
              updatePersonaMutation.mutate({
                personaId: persona.persona_id,
                data,
              });
            }
          }}
          isLoading={updatePersonaMutation.isPending}
        />
      )}

      {npc && (
        <NPCConfigDialog
          npc={npc}
          open={showConfigDialog}
          onOpenChange={setShowConfigDialog}
          onSave={(config) => {
            updateConfigMutation.mutate(config);
          }}
          isLoading={updateConfigMutation.isPending}
        />
      )}
    </div>
  );
}

interface PersonaEditDialogProps {
  persona: PersonaProfile;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (data: Partial<PersonaProfile>) => void;
  isLoading: boolean;
}

function PersonaEditDialog({ persona, open, onOpenChange, onSave, isLoading }: PersonaEditDialogProps) {
  const [name, setName] = useState(persona.name);
  const [traits, setTraits] = useState(persona.traits.join(', '));
  const [habits, setHabits] = useState(persona.habits.join(', '));
  const [goals, setGoals] = useState(persona.goals.join(', '));
  const [background, setBackground] = useState(persona.background);
  const [speechStyle, setSpeechStyle] = useState(persona.speech_style);

  useEffect(() => {
    if (open) {
      setName(persona.name);
      setTraits(persona.traits.join(', '));
      setHabits(persona.habits.join(', '));
      setGoals(persona.goals.join(', '));
      setBackground(persona.background);
      setSpeechStyle(persona.speech_style);
    }
  }, [open, persona]);

  const handleSave = () => {
    onSave({
      name,
      traits: traits.split(',').map((t) => t.trim()).filter(Boolean),
      habits: habits.split(',').map((h) => h.trim()).filter(Boolean),
      goals: goals.split(',').map((g) => g.trim()).filter(Boolean),
      background,
      speech_style: speechStyle,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Persona: {persona.name}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="edit-name">Name</Label>
            <Input
              id="edit-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Persona name"
            />
          </div>

          <div>
            <Label htmlFor="edit-traits">Traits (comma-separated)</Label>
            <Input
              id="edit-traits"
              value={traits}
              onChange={(e) => setTraits(e.target.value)}
              placeholder="wise, patient, protective"
            />
          </div>

          <div>
            <Label htmlFor="edit-habits">Habits (comma-separated)</Label>
            <Input
              id="edit-habits"
              value={habits}
              onChange={(e) => setHabits(e.target.value)}
              placeholder="smoking pipe, speaking in riddles"
            />
          </div>

          <div>
            <Label htmlFor="edit-goals">Goals (comma-separated)</Label>
            <Input
              id="edit-goals"
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              placeholder="protect the innocent, guide the hero"
            />
          </div>

          <div>
            <Label htmlFor="edit-background">Background</Label>
            <Textarea
              id="edit-background"
              value={background}
              onChange={(e) => setBackground(e.target.value)}
              placeholder="Background story..."
              rows={4}
            />
          </div>

          <div>
            <Label htmlFor="edit-speech">Speech Style</Label>
            <Textarea
              id="edit-speech"
              value={speechStyle}
              onChange={(e) => setSpeechStyle(e.target.value)}
              placeholder="How this persona speaks..."
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface NPCConfigDialogProps {
  npc: NPC;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (config: NPCConfig) => void;
  isLoading: boolean;
}

function NPCConfigDialog({ npc, open, onOpenChange, onSave, isLoading }: NPCConfigDialogProps) {
  const defaultConfig: NPCConfig = {
    retrieval_top_k: 5,
    importance_threshold: 0.7,
    reflection_threshold: 0.7,
    max_facts_per_dimension: 3,
  };

  const [config, setConfig] = useState<NPCConfig>(npc.config || defaultConfig);

  useEffect(() => {
    if (open) {
      setConfig(npc.config || defaultConfig);
    }
  }, [open, npc.config]);

  const handleSave = () => {
    onSave(config);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>NPC Configuration: {npc.name}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div>
            <Label htmlFor="retrieval_top_k">
              Retrieval Top K (각 인덱스당 검색할 메모리 개수)
            </Label>
            <Input
              id="retrieval_top_k"
              type="number"
              min="1"
              max="20"
              value={config.retrieval_top_k}
              onChange={(e) =>
                setConfig({ ...config, retrieval_top_k: parseInt(e.target.value) || 5 })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">범위: 1-20 (기본값: 5)</p>
          </div>

          <div>
            <Label htmlFor="importance_threshold">
              Importance Threshold (장기 기억 전환 임계값)
            </Label>
            <Input
              id="importance_threshold"
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={config.importance_threshold}
              onChange={(e) =>
                setConfig({ ...config, importance_threshold: parseFloat(e.target.value) || 0.7 })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              범위: 0.0-1.0 (기본값: 0.7 = 70%)
            </p>
          </div>

          <div>
            <Label htmlFor="reflection_threshold">
              Reflection Threshold (Reflection 트리거 임계값)
            </Label>
            <Input
              id="reflection_threshold"
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={config.reflection_threshold}
              onChange={(e) =>
                setConfig({ ...config, reflection_threshold: parseFloat(e.target.value) || 0.7 })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              범위: 0.0-1.0 (기본값: 0.7 = 70%)
            </p>
          </div>

          <div>
            <Label htmlFor="max_facts_per_dimension">
              Max Facts Per Dimension (Dimension당 최대 fact 개수)
            </Label>
            <Input
              id="max_facts_per_dimension"
              type="number"
              min="1"
              max="10"
              value={config.max_facts_per_dimension}
              onChange={(e) =>
                setConfig({ ...config, max_facts_per_dimension: parseInt(e.target.value) || 3 })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">범위: 1-10 (기본값: 3)</p>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isLoading}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              {isLoading ? 'Saving...' : 'Save Configuration'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
