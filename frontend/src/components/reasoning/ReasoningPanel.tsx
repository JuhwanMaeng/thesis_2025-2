import { useState, useMemo } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp, Wrench, FileText, ArrowRight, Trash2, Brain, Search, Database, Code } from 'lucide-react';
import { format } from 'date-fns';
import type { InferenceTrace } from '@/types';
import { Badge } from '@/components/ui/badge';
import { traceApi } from '@/services/api';
import { Button } from '@/components/ui/button';

interface ReasoningPanelProps {
  npcId: string | null;
  trace?: InferenceTrace | null;
}

export function ReasoningPanel({ npcId }: ReasoningPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: traces = [], isLoading } = useQuery<InferenceTrace[]>({
    queryKey: ['traces', npcId],
    queryFn: () => traceApi.getByNpc(npcId!, 100),
    enabled: !!npcId,
    retry: false,
  });

  // 시간순으로 정렬 (최신이 위에)
  const sortedTraces = useMemo(() => {
    return [...traces].sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return dateB - dateA; // 내림차순 (최신이 위)
    });
  }, [traces]);

  const deleteTraceMutation = useMutation({
    mutationFn: (traceId: string) => traceApi.delete(traceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces', npcId] });
      if (selectedTraceId) {
        setSelectedTraceId(null);
      }
    },
  });

  const deleteAllTracesMutation = useMutation({
    mutationFn: () => traceApi.deleteByNpc(npcId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces', npcId] });
      setSelectedTraceId(null);
    },
  });

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full flex flex-col border-t border-border bg-card">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Reasoning & Traces</span>
          {sortedTraces.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {sortedTraces.length} trace{sortedTraces.length !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 rounded hover:bg-secondary transition-colors"
        >
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          )}
        </button>
      </div>

      {isExpanded && (
        <div className="flex-1 min-h-0 overflow-y-auto scrollbar-thin">
          <div className="px-4 py-3 space-y-2">
            {isLoading ? (
              <div className="text-center text-sm text-muted-foreground py-4">Loading...</div>
            ) : sortedTraces.length === 0 ? (
              <div className="text-center text-sm text-muted-foreground py-8">
                No traces yet. Send messages to generate traces.
              </div>
            ) : (
              <>
                {sortedTraces.length > 0 && (
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-muted-foreground">
                      {sortedTraces.length} trace{sortedTraces.length !== 1 ? 's' : ''}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs text-destructive hover:text-destructive"
                      onClick={() => {
                        if (confirm(`Delete all ${sortedTraces.length} traces?`)) {
                          deleteAllTracesMutation.mutate();
                        }
                      }}
                      disabled={deleteAllTracesMutation.isPending}
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Clear All
                    </Button>
                  </div>
                )}
                {sortedTraces.map((trace) => {
                  const isTraceExpanded = selectedTraceId === trace.trace_id;
                  return (
                    <div
                      key={trace.trace_id}
                      className={cn(
                        'rounded-lg border transition-colors group',
                        isTraceExpanded
                          ? 'bg-primary/5 border-primary'
                          : 'bg-secondary/50 border-border/50 hover:bg-secondary'
                      )}
                    >
                      <div
                        className="p-3 cursor-pointer"
                        onClick={() => setSelectedTraceId(isTraceExpanded ? null : trace.trace_id)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <ChevronDown className={cn(
                              "w-3 h-3 text-muted-foreground transition-transform",
                              isTraceExpanded && "transform rotate-180"
                            )} />
                            <Badge variant="outline" className="text-xs">
                              {trace.chosen_action}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {format(new Date(trace.created_at), 'yyyy-MM-dd HH:mm:ss')}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            {isTraceExpanded ? (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedTraceId(null);
                                }}
                                className="p-0.5 rounded hover:bg-secondary"
                                title="Collapse"
                              >
                                <ChevronUp className="w-3 h-3" />
                              </button>
                            ) : (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (confirm('Delete this trace?')) {
                                    deleteTraceMutation.mutate(trace.trace_id);
                                  }
                                }}
                                className="p-0.5 rounded hover:bg-destructive/20 text-destructive"
                                title="Delete trace"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground truncate">
                          {typeof trace.observation === 'string' 
                            ? trace.observation 
                            : trace.observation 
                              ? JSON.stringify(trace.observation) 
                              : 'No observation'}
                        </div>
                      </div>
                      {isTraceExpanded && (
                        <div className="px-3 pb-3 border-t border-border/50 pt-3">
                          <TraceDetail trace={trace} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function TraceDetail({ trace }: { trace: InferenceTrace }) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    retrieval: true,
    prompt: false,
    fullResult: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="space-y-3">
      {/* Observation */}
      <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
        <div className="text-xs font-medium text-muted-foreground flex items-center gap-2">
          <Search className="w-3 h-3" />
          Observation
        </div>
        <div className="text-sm">
          {typeof trace.observation === 'string' 
            ? trace.observation 
            : trace.observation 
              ? JSON.stringify(trace.observation, null, 2) 
              : 'No observation'}
        </div>
      </div>

      {/* Retrieval Details */}
      {(trace.retrieved_memories?.length > 0 || trace.retrieval_query_text || trace.retrieval_indices_searched?.length > 0) && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <button
            onClick={() => toggleSection('retrieval')}
            className="w-full flex items-center justify-between text-xs font-medium text-muted-foreground"
          >
            <div className="flex items-center gap-2">
              <Database className="w-3 h-3" />
              Memory Retrieval
              {trace.retrieved_memories && (
                <Badge variant="outline" className="text-xs">
                  {trace.retrieved_memories.length} memories
                </Badge>
              )}
            </div>
            {expandedSections.retrieval ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {expandedSections.retrieval && (
            <div className="space-y-2 pt-2">
              {trace.retrieval_query_text && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Query:</div>
                  <div className="text-xs font-mono bg-background p-2 rounded">{trace.retrieval_query_text}</div>
                </div>
              )}
              {trace.retrieval_indices_searched && trace.retrieval_indices_searched.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Indices Searched:</div>
                  <div className="flex flex-wrap gap-1">
                    {trace.retrieval_indices_searched.map((idx, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {idx}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {trace.retrieved_memories && trace.retrieved_memories.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Memory IDs:</div>
                  <div className="flex flex-wrap gap-1">
                    {trace.retrieved_memories.map((memId, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs font-mono">
                        {typeof memId === 'string' ? memId : JSON.stringify(memId)}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {trace.retrieval_similarity_scores && trace.retrieval_similarity_scores.length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Similarity Scores:</div>
                  <div className="flex flex-wrap gap-1">
                    {trace.retrieval_similarity_scores.map((score, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {(score * 100).toFixed(1)}%
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Persona & World Context */}
      {(trace.persona_used || trace.world_used) && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <div className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <Brain className="w-3 h-3" />
            Context Used
          </div>
          <div className="space-y-1 text-xs">
            {trace.persona_used && (
              <div>
                <span className="text-muted-foreground">Persona:</span>{' '}
                <span className="font-mono">{trace.persona_used}</span>
              </div>
            )}
            {trace.world_used && (
              <div>
                <span className="text-muted-foreground">World:</span>{' '}
                <span className="font-mono">{trace.world_used}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action & Tool */}
      <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-primary" />
            <span className="text-sm font-mono font-medium">{trace.chosen_action}</span>
          </div>
        </div>
        {trace.tool_arguments && (
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Arguments:</div>
            <code className="block text-xs font-mono bg-background p-2 rounded overflow-x-auto">
              {JSON.stringify(trace.tool_arguments, null, 2)}
            </code>
          </div>
        )}
        {trace.tool_execution_result && (
          <div className="space-y-1 pt-2">
            <div className="flex items-center gap-2">
              <ArrowRight className="w-3 h-3 text-muted-foreground" />
              <span className="text-xs font-medium text-muted-foreground">Execution Result:</span>
              <Badge variant={trace.tool_execution_result.success ? 'default' : 'destructive'} className="text-xs">
                {trace.tool_execution_result.success ? 'Success' : 'Failed'}
              </Badge>
            </div>
            {!trace.tool_execution_result.success && (
              <div className="text-xs text-destructive font-mono bg-destructive/10 p-2 rounded mt-1 border border-destructive/20">
                <div className="font-semibold mb-1">Error:</div>
                {trace.tool_execution_result.error || 'Unknown error occurred'}
              </div>
            )}
            {trace.tool_execution_result.effect && Object.keys(trace.tool_execution_result.effect).length > 0 && (
              <div className="space-y-1 mt-1">
                <div className="text-xs text-muted-foreground">Effect:</div>
                <div className="text-xs font-mono bg-background p-2 rounded border border-border/50">
                  {JSON.stringify(trace.tool_execution_result.effect, null, 2)}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* LLM Reasoning */}
      {trace.llm_output_raw && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <div className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <Brain className="w-3 h-3" />
            LLM Reasoning
          </div>
          <div className="text-sm whitespace-pre-wrap max-h-48 overflow-y-auto scrollbar-thin">
            {trace.llm_output_raw}
          </div>
        </div>
      )}

      {/* Full Prompt Snapshot */}
      {trace.llm_prompt_snapshot && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <button
            onClick={() => toggleSection('prompt')}
            className="w-full flex items-center justify-between text-xs font-medium text-muted-foreground"
          >
            <div className="flex items-center gap-2">
              <Code className="w-3 h-3" />
              Full Prompt Snapshot
            </div>
            {expandedSections.prompt ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {expandedSections.prompt && (
            <div className="text-xs font-mono bg-background p-2 rounded max-h-64 overflow-y-auto scrollbar-thin whitespace-pre-wrap mt-2">
              {trace.llm_prompt_snapshot}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
