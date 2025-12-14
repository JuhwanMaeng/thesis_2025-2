import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp, Wrench, Clock, FileText, ArrowRight, List, X } from 'lucide-react';
import { format } from 'date-fns';
import type { InferenceTrace } from '@/types';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { traceApi } from '@/services/api';

interface ReasoningPanelProps {
  npcId: string | null;
  trace?: InferenceTrace | null;
}

export function ReasoningPanel({ npcId, trace: latestTrace }: ReasoningPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

  const { data: traces = [], isLoading } = useQuery<InferenceTrace[]>({
    queryKey: ['traces', npcId],
    queryFn: () => traceApi.getByNpc(npcId!, 50),
    enabled: !!npcId,
    retry: false,
  });

  const displayTrace = selectedTraceId
    ? traces.find((t) => t.trace_id === selectedTraceId) || latestTrace
    : latestTrace;

  if (!npcId) {
    return null;
  }

  return (
    <div className="h-full flex flex-col border-t border-border bg-card">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border shrink-0">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Reasoning & Traces</span>
          {displayTrace && (
            <Badge variant="outline" className="text-xs">
              {displayTrace.chosen_action}
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
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <Tabs defaultValue="current" className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <TabsList className="mx-4 mt-2 shrink-0">
            <TabsTrigger value="current" className="text-xs">Current</TabsTrigger>
            <TabsTrigger value="history" className="text-xs">
              History ({traces.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="current" className="flex-1 min-h-0 overflow-y-auto scrollbar-thin mt-0">
            <div className="px-4 py-3 space-y-3">
              {displayTrace ? (
                <TraceDetail trace={displayTrace} />
              ) : (
                <div className="text-center text-sm text-muted-foreground py-8">
                  No reasoning data available. Send a message to see reasoning.
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="history" className="flex-1 min-h-0 overflow-y-auto scrollbar-thin mt-0">
            <div className="px-4 py-3 space-y-2">
              {isLoading ? (
                <div className="text-center text-sm text-muted-foreground py-4">Loading...</div>
              ) : traces.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground py-8">
                  No traces yet. Send messages to generate traces.
                </div>
              ) : (
                <>
                  {traces.map((trace) => (
                    <div
                      key={trace.trace_id}
                      className={cn(
                        'p-3 rounded-lg border cursor-pointer transition-colors',
                        selectedTraceId === trace.trace_id
                          ? 'bg-primary/10 border-primary'
                          : 'bg-secondary/50 border-border/50 hover:bg-secondary'
                      )}
                      onClick={() => setSelectedTraceId(trace.trace_id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {trace.chosen_action}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {format(new Date(trace.created_at), 'HH:mm:ss')}
                          </span>
                        </div>
                        {selectedTraceId === trace.trace_id && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedTraceId(null);
                            }}
                            className="p-0.5 rounded hover:bg-secondary"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground truncate">
                        {trace.observation || 'No observation'}
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
          </TabsContent>
        </Tabs>
        </div>
      )}
    </div>
  );
}

function TraceDetail({ trace }: { trace: InferenceTrace }) {
  return (
    <div className="space-y-3">
      <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
        <div className="text-xs font-medium text-muted-foreground">Observation</div>
        <div className="text-sm">{trace.observation}</div>
      </div>

      {trace.retrieved_memories && trace.retrieved_memories.length > 0 && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <div className="text-xs font-medium text-muted-foreground">
            Retrieved Memories ({trace.retrieved_memories.length})
          </div>
          <div className="flex flex-wrap gap-1">
            {trace.retrieved_memories.map((memId, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {typeof memId === 'string' ? memId : JSON.stringify(memId)}
              </Badge>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-3.5 h-3.5 text-primary" />
            <span className="text-sm font-mono font-medium">{trace.chosen_action}</span>
          </div>
        </div>
        {trace.tool_arguments && (
          <div className="flex items-start gap-2 text-xs font-mono">
            <span className="text-muted-foreground shrink-0">Args:</span>
            <code className="flex-1 text-foreground/80 break-all">
              {JSON.stringify(trace.tool_arguments, null, 2)}
            </code>
          </div>
        )}
        {trace.tool_execution_result && (
          <>
            <div className="flex items-center gap-2">
              <ArrowRight className="w-3 h-3 text-muted-foreground" />
            </div>
            <div className="flex items-start gap-2 text-xs font-mono">
              <span className="text-muted-foreground shrink-0">Result:</span>
              <code className="flex-1 text-success break-all">
                {trace.tool_execution_result.success ? 'Success' : 'Failed'}
              </code>
            </div>
          </>
        )}
      </div>

      {trace.llm_output_raw && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border/50 space-y-2">
          <div className="text-xs font-medium text-muted-foreground">Reasoning</div>
          <div className="text-sm whitespace-pre-wrap max-h-32 overflow-y-auto">
            {trace.llm_output_raw}
          </div>
        </div>
      )}
    </div>
  );
}
