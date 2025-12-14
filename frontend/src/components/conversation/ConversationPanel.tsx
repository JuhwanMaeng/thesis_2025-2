import { useState, useRef, useEffect, useMemo } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import { turnApi, npcApi, traceApi } from '@/services/api';
import type { Message, TurnResult, InferenceTrace, NPC } from '@/types';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { cn } from '@/lib/utils';

interface ConversationPanelProps {
  npcId: string | null;
  npcName?: string;
  onTraceGenerated?: (trace: InferenceTrace) => void;
  onExpandedChange?: (expanded: boolean) => void;
  isFullPage?: boolean;
}

export function ConversationPanel({ npcId, npcName, onTraceGenerated, onExpandedChange, isFullPage = false }: ConversationPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(isFullPage);
  const scrollRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // NPC 정보 조회 (location 등 current_state 접근용)
  const { data: npc } = useQuery<NPC>({
    queryKey: ['npc', npcId],
    queryFn: () => npcApi.get(npcId!),
    enabled: !!npcId,
  });

  // Trace에서 대화 히스토리 복원 (최근 50개만)
  const { data: traces = [] } = useQuery<InferenceTrace[]>({
    queryKey: ['traces', npcId],
    queryFn: () => traceApi.getByNpc(npcId!, 50),
    enabled: !!npcId,
    staleTime: 5000, // 5초간 캐시 유지
  });

  // Trace에서 메시지 히스토리 복원 (useMemo로 최적화)
  const restoredMessages = useMemo(() => {
    if (!npcId || traces.length === 0) {
      return [];
    }

    // 시간순으로 정렬 (오래된 것부터)
    const sortedTraces = [...traces].sort((a, b) => {
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    });

    const messages: Message[] = [];
    const existingTraceIds = new Set<string>();

    sortedTraces.forEach((trace) => {
      // 사용자 메시지 (observation에서 추출)
      // observation 형식: "player_001 said: 'hi' at shire" 또는 단순 텍스트
      let userContent = trace.observation || '';
      
      // "said:" 형식 파싱
      if (userContent.includes('said:')) {
        const match = userContent.match(/said:\s*["']?([^"']+)["']?/i);
        if (match && match[1]) {
          userContent = match[1].trim();
        }
      }
      
      if (userContent && !existingTraceIds.has(`${trace.trace_id}_user`)) {
        messages.push({
          id: `msg_${trace.trace_id}_user`,
          role: 'user',
          content: userContent,
          timestamp: new Date(trace.created_at),
        });
        existingTraceIds.add(`${trace.trace_id}_user`);
      }

      // NPC 메시지 (tool_execution_result.effect.utterance에서 추출)
      const toolResult = trace.tool_execution_result;
      const npcUtterance = toolResult?.effect?.utterance;
      
      if (npcUtterance && trace.chosen_action === 'talk' && !existingTraceIds.has(`${trace.trace_id}_agent`)) {
        messages.push({
          id: `msg_${trace.trace_id}_agent`,
          role: 'agent',
          content: npcUtterance,
          timestamp: new Date(trace.created_at),
          action: {
            action_type: trace.chosen_action,
            arguments: trace.tool_arguments || {},
            reason: trace.llm_output_raw || '',
          },
          trace_id: trace.trace_id,
        });
        existingTraceIds.add(`${trace.trace_id}_agent`);
      }
    });

    return messages;
  }, [npcId, traces]);

  // restoredMessages가 변경될 때만 메시지 업데이트
  useEffect(() => {
    if (npcId) {
      setMessages(restoredMessages);
    } else {
      setMessages([]);
    }
  }, [npcId, restoredMessages]);

  const handleToggle = () => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    if (onExpandedChange) {
      onExpandedChange(newExpanded);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (content: string) => {
    if (!npcId) return;

    if (!isExpanded) {
      setIsExpanded(true);
      if (onExpandedChange) {
        onExpandedChange(true);
      }
    }

    // 사용자 메시지는 trace가 생성되면 자동으로 복원되므로 여기서는 추가하지 않음
    // (optimistic update는 trace가 빠르게 업데이트되므로 불필요)

    setIsLoading(true);

    try {
      // NPC의 현재 위치를 가져오거나 기본값 사용
      const currentLocation = npc?.current_state?.location || 'unknown';
      
      const observation = {
        event_type: 'player_interaction',
        actor: 'player_001',
        action: content,
        location: currentLocation,
        details: {
          dialogue: content,
        },
      };

      const result: TurnResult = await turnApi.run(npcId, observation);

      // NPC 응답 메시지 즉시 추가 (optimistic update)
      const npcUtterance = result.result?.effect?.utterance;
      
      if (npcUtterance) {
        const agentMessage: Message = {
          id: `msg_${result.trace_id}_agent`,
          role: 'agent',
          content: npcUtterance,
          timestamp: new Date(),
          action: result.action,
          trace_id: result.trace_id,
        };
        setMessages((prev) => {
          const exists = prev.some(msg => msg.id === agentMessage.id);
          return exists ? prev : [...prev, agentMessage];
        });
      }

      // trace가 업데이트되면 useMemo에서 자동으로 복원됨
      // query를 invalidate하여 trace를 다시 불러오도록 함
      queryClient.invalidateQueries({ queryKey: ['traces', npcId] });

      if (onTraceGenerated) {
        const partialTrace: InferenceTrace = {
          trace_id: result.trace_id,
          npc_id: npcId,
          turn_id: result.turn_id,
          observation: observation.action || '',
          retrieved_memories: [],
          retrieval_query_text: '',
          retrieval_indices_searched: [],
          retrieval_vector_ids: [],
          retrieval_similarity_scores: [],
          persona_used: null,
          world_used: null,
          llm_prompt_snapshot: '',
          llm_output_raw: result.reason,
          chosen_action: result.action.action_type,
          tool_arguments: result.action.arguments,
          tool_execution_result: result.result,
          created_at: new Date().toISOString(),
        };
        onTraceGenerated(partialTrace);
      }

      queryClient.invalidateQueries({ queryKey: ['memories', npcId] });
      queryClient.invalidateQueries({ queryKey: ['traces', npcId] });
    } catch (error) {
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!npcId) {
    return (
      <div className="flex flex-col h-full bg-background items-center justify-center">
        <MessageSquare className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">Select an NPC to start conversation</p>
      </div>
    );
  }

  // 전체 페이지 모드일 때는 항상 확장
  const shouldShowContent = isFullPage || isExpanded;

  return (
    <div className="flex flex-col h-full bg-background">
      {!isFullPage && (
        <button
          onClick={handleToggle}
          className="h-12 flex items-center justify-between px-4 bg-card shrink-0 hover:bg-secondary/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <MessageSquare className="w-4 h-4 text-muted-foreground" />
            <h2 className="text-sm font-medium">{npcName || 'NPC Conversation'}</h2>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">
              {messages.length} messages
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            )}
          </div>
        </button>
      )}

      {shouldShowContent && (
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          <div
            ref={scrollRef}
            className="flex-1 min-h-0 overflow-y-auto scrollbar-thin flex flex-col"
          >
            <div className="flex-1 flex items-center justify-center px-4 py-4">
              {messages.length === 0 ? (
                <div className="text-center text-muted-foreground">
                  <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Start a conversation</p>
                </div>
              ) : (
                <div className="w-full space-y-4">
                  {messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="shrink-0 border-t border-border bg-card">
            <ChatInput onSend={handleSend} isLoading={isLoading} />
          </div>
        </div>
      )}
    </div>
  );
}
