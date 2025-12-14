import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import { turnApi } from '@/services/api';
import type { Message, TurnResult, InferenceTrace } from '@/types';
import { useQueryClient } from '@tanstack/react-query';
import { cn } from '@/lib/utils';

interface ConversationPanelProps {
  npcId: string | null;
  npcName?: string;
  onTraceGenerated?: (trace: InferenceTrace) => void;
  onExpandedChange?: (expanded: boolean) => void;
}

export function ConversationPanel({ npcId, npcName, onTraceGenerated, onExpandedChange }: ConversationPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

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

  useEffect(() => {
    setMessages([]);
  }, [npcId]);

  const handleSend = async (content: string) => {
    if (!npcId) return;

    if (!isExpanded) {
      setIsExpanded(true);
      if (onExpandedChange) {
        onExpandedChange(true);
      }
    }

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);

    try {
      const observation = {
        event_type: 'player_interaction',
        actor: 'player_001',
        action: content,
        location: 'unknown',
        details: {
          dialogue: content,
        },
      };

      const result: TurnResult = await turnApi.run(npcId, observation);

      const agentMessage: Message = {
        id: `msg_${Date.now()}_agent`,
        role: 'agent',
        content: result.result.effect.utterance || result.reason || 'Action executed',
        timestamp: new Date(),
        action: result.action,
        trace_id: result.trace_id,
      };
      setMessages((prev) => [...prev, agentMessage]);

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
      console.error('Failed to send message:', error);
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

  return (
    <div className="flex flex-col h-full bg-background">
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

      {isExpanded && (
        <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
          <div
            ref={scrollRef}
            className="flex-1 min-h-0 overflow-y-auto scrollbar-thin"
          >
            <div className="px-4 py-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center min-h-[200px] text-muted-foreground">
                  <div className="text-center">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Start a conversation</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
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
