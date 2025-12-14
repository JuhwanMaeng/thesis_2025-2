
export interface NPCConfig {
  retrieval_top_k: number;
  importance_threshold: number;
  reflection_threshold: number;
  max_facts_per_dimension: number;
}

export interface NPC {
  npc_id: string;
  name: string;
  role: string;
  persona_id: string;
  world_id: string;
  current_state: {
    emotion?: string;
    goal?: string;
    location?: string;
    hp?: number;
    status_flags?: string[];
    [key: string]: any;
  };
  config?: NPCConfig;
  created_at: string;
  updated_at: string;
}

export interface PersonaProfile {
  persona_id: string;
  name: string;
  traits: string[];
  habits: string[];
  goals: string[];
  background: string;
  speech_style: string;
  relationships: Record<string, string>;
  constraints: {
    taboos?: string[];
    moral_rules?: string[];
    [key: string]: any;
  };
}

export interface WorldKnowledge {
  world_id: string;
  title: string;
  rules: {
    laws?: string[];
    factions?: Record<string, string>;
    social_norms?: string[];
    [key: string]: any;
  };
  locations: Record<string, any>;
  danger_levels: Record<string, number>;
  global_constraints: Record<string, any>;
}

export interface EpisodicMemory {
  memory_id: string;
  npc_id: string;
  memory_type: 'short_term' | 'long_term';
  content: string;
  source: 'observation' | 'action' | 'reflection';
  importance: number;
  tags: string[];
  linked_entities: string[];
  created_at: string;
}

export interface InferenceTrace {
  trace_id: string;
  npc_id: string;
  turn_id: string;
  observation: string;
  retrieved_memories: string[];
  retrieval_query_text: string;
  retrieval_indices_searched: string[];
  retrieval_vector_ids: number[];
  retrieval_similarity_scores: number[];
  persona_used: string | null;
  world_used: string | null;
  llm_prompt_snapshot: string;
  llm_output_raw: string;
  chosen_action: string;
  tool_arguments: Record<string, any>;
  tool_execution_result: {
    success: boolean;
    action_type: string;
    effect: Record<string, any>;
    error?: string;
  };
  created_at: string;
}

export interface Action {
  action_type: string;
  arguments: Record<string, any>;
  reason: string;
}

export interface TurnResult {
  action: Action;
  result: {
    success: boolean;
    action_type: string;
    effect: Record<string, any>;
    error?: string;
  };
  reason: string;
  trace_id: string;
  turn_id: string;
  importance_score: number;
  importance_justification: string;
  reflection_used: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  action?: Action;
  trace_id?: string;
}

export interface VectorMemoryResult {
  query_text: string;
  indices_searched: string[];
  top_k: number;
  retrieved_vector_ids: number[];
  retrieved_sources: Array<{
    vector_id: number;
    source_type: 'episodic' | 'persona' | 'world';
    source_id: string;
    npc_id?: string;
    importance: number;
    created_at: string;
    summary: string;
    similarity_score: number;
  }>;
  similarity_scores: number[];
}
