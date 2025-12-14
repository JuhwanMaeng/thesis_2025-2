import axios from 'axios';
import type {
  NPC,
  NPCConfig,
  PersonaProfile,
  WorldKnowledge,
  EpisodicMemory,
  InferenceTrace,
  TurnResult,
  VectorMemoryResult,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// NPC API
export const npcApi = {
  create: async (data: {
    name: string;
    role: string;
    persona_id: string;
    world_id: string;
    current_state?: Record<string, any>;
    config?: Partial<NPCConfig>;
  }): Promise<NPC> => {
    const response = await api.post('/npc/create', data);
    return response.data;
  },

  get: async (npcId: string): Promise<NPC> => {
    const response = await api.get(`/npc/${npcId}`);
    return response.data;
  },

  list: async (limit = 100): Promise<NPC[]> => {
    const response = await api.get('/npc', { params: { limit } });
    return response.data;
  },
  delete: async (npcId: string): Promise<{ status: string; npc_id: string }> => {
    const response = await api.delete(`/npc/${npcId}`);
    return response.data;
  },
  update: async (npcId: string, updates: Partial<NPC>): Promise<NPC> => {
    const response = await api.put(`/npc/${npcId}`, updates);
    return response.data;
  },
  updateConfig: async (npcId: string, config: NPCConfig): Promise<NPC> => {
    const response = await api.put(`/npc/${npcId}/config`, config);
    return response.data;
  },
  generate: async (data: {
    description: string;
    role?: string;
    config?: Partial<NPCConfig>;
  }): Promise<{ npc: NPC; persona: any; world: any }> => {
    const response = await api.post('/npc/generate', data);
    return response.data;
  },
};

// Memory API
export const memoryApi = {
  create: async (npcId: string, data: {
    content: string;
    source?: 'observation' | 'action' | 'reflection';
    importance?: number;
    tags?: string[];
    linked_entities?: string[];
  }): Promise<EpisodicMemory> => {
    const response = await api.post(`/npc/${npcId}/memory`, data);
    return response.data;
  },

  getRecent: async (npcId: string, limit = 50, memoryType?: 'short_term' | 'long_term'): Promise<EpisodicMemory[]> => {
    const response = await api.get(`/npc/${npcId}/memory/recent`, {
      params: { limit, memory_type: memoryType },
    });
    return response.data;
  },

  getAll: async (npcId: string, limit = 50, memoryType?: 'short_term' | 'long_term'): Promise<EpisodicMemory[]> => {
    const response = await api.get(`/npc/${npcId}/memory`, {
      params: { limit, memory_type: memoryType },
    });
    return response.data;
  },
  delete: async (npcId: string, memoryId: string): Promise<{ status: string; memory_id: string }> => {
    const response = await api.delete(`/npc/${npcId}/memory/${memoryId}`);
    return response.data;
  },
  deleteByNpc: async (npcId: string, memoryType?: 'short_term' | 'long_term'): Promise<{ status: string; npc_id: string; deleted_count: number }> => {
    const response = await api.delete(`/npc/${npcId}/memory`, {
      params: memoryType ? { memory_type: memoryType } : {},
    });
    return response.data;
  },
};

// Turn API
export const turnApi = {
  run: async (npcId: string, observation: Record<string, any>, turnId?: string): Promise<TurnResult> => {
    const response = await api.post(`/npc/${npcId}/turn`, observation, {
      params: turnId ? { turn_id: turnId } : {},
    });
    return response.data;
  },
};

// Vector Memory API
export const vectorApi = {
  getMemories: async (npcId: string, query?: string, topK = 10): Promise<VectorMemoryResult> => {
    const response = await api.get(`/npc/${npcId}/vector_memories`, {
      params: { query, top_k: topK },
    });
    return response.data;
  },

  reindex: async (indexType: 'episodic' | 'persona' | 'world'): Promise<{ status: string; vectors_indexed: number }> => {
    const response = await api.post('/vector/reindex', null, {
      params: { index_type: indexType },
    });
    return response.data;
  },

  getStats: async (): Promise<{
    episodic: { vector_count: number; index_exists: boolean; metadata_exists: boolean };
    persona: { vector_count: number; index_exists: boolean; metadata_exists: boolean };
    world: { vector_count: number; index_exists: boolean; metadata_exists: boolean };
  }> => {
    const response = await api.get('/vector/stats');
    return response.data;
  },
};

// Tools API
export const toolsApi = {
  list: async (): Promise<{ tools: any[]; tool_names: string[]; count: number }> => {
    const response = await api.get('/tools');
    return response.data;
  },
  listDynamic: async (): Promise<any[]> => {
    const response = await api.get('/tool');
    return response.data;
  },
  create: async (data: {
    name: string;
    description: string;
    parameters_schema: Record<string, any>;
    code: string;
  }): Promise<any> => {
    const response = await api.post('/tool/create', data);
    return response.data;
  },
  update: async (toolId: string, updates: Partial<any>): Promise<any> => {
    const response = await api.put(`/tool/${toolId}`, updates);
    return response.data;
  },
  delete: async (toolId: string): Promise<{ status: string; tool_id: string }> => {
    const response = await api.delete(`/tool/${toolId}`);
    return response.data;
  },
};

// Persona API
export const personaApi = {
  get: async (personaId: string): Promise<PersonaProfile> => {
    const response = await api.get(`/persona/${personaId}`);
    return response.data;
  },
  update: async (personaId: string, data: Partial<PersonaProfile>): Promise<PersonaProfile> => {
    const response = await api.put(`/persona/${personaId}`, data);
    return response.data;
  },
};

// World API
export const worldApi = {
  list: async (): Promise<WorldKnowledge[]> => {
    const response = await api.get('/world');
    return response.data;
  },
  get: async (worldId: string): Promise<WorldKnowledge> => {
    const response = await api.get(`/world/${worldId}`);
    return response.data;
  },
  create: async (data: {
    world_id?: string;
    title: string;
    rules?: Record<string, any>;
    locations?: Record<string, any>;
    danger_levels?: Record<string, number>;
    global_constraints?: Record<string, any>;
  }): Promise<WorldKnowledge> => {
    const response = await api.post('/world/create', data);
    return response.data;
  },
  update: async (worldId: string, updates: Partial<WorldKnowledge>): Promise<WorldKnowledge> => {
    const response = await api.put(`/world/${worldId}`, updates);
    return response.data;
  },
  delete: async (worldId: string, deleteNpcs: boolean = false): Promise<{ status: string; world_id: string; deleted_npcs: number }> => {
    const response = await api.delete(`/world/${worldId}`, {
      params: { delete_npcs: deleteNpcs }
    });
    return response.data;
  },
  getNpcs: async (worldId: string): Promise<NPC[]> => {
    const response = await api.get(`/world/${worldId}/npcs`);
    return response.data;
  },
};

// Trace API
export const traceApi = {
  getByNpc: async (npcId: string, limit = 50, offset = 0): Promise<InferenceTrace[]> => {
    const response = await api.get(`/npc/${npcId}/traces`, { params: { limit, offset } });
    return response.data;
  },
  get: async (traceId: string): Promise<InferenceTrace> => {
    const response = await api.get(`/trace/${traceId}`);
    return response.data;
  },
  delete: async (traceId: string): Promise<{ status: string; trace_id: string }> => {
    const response = await api.delete(`/trace/${traceId}`);
    return response.data;
  },
  deleteByNpc: async (npcId: string): Promise<{ status: string; npc_id: string; deleted_count: number }> => {
    const response = await api.delete(`/npc/${npcId}/traces`);
    return response.data;
  },
};

export default api;
