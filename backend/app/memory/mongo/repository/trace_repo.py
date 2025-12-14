"""Inference trace repository - CRUD 작업만."""
from typing import List, Optional
from datetime import datetime
import uuid
from app.memory.mongo.client import get_collection
from app.schemas.trace import InferenceTrace, TraceCreate


class TraceRepository:
    """Inference trace 작업 repository."""
    
    @staticmethod
    def _get_collection():
        return get_collection("inference_traces")
    
    @staticmethod
    def insert_trace(trace_data: TraceCreate) -> InferenceTrace:
        """Inference trace 삽입."""
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        trace_doc = {
            "trace_id": trace_id,
            "npc_id": trace_data.npc_id,
            "turn_id": trace_data.turn_id,
            "observation": trace_data.observation,
            "retrieved_memories": trace_data.retrieved_memories,
            "persona_used": trace_data.persona_used,
            "world_used": trace_data.world_used,
            "llm_prompt_snapshot": trace_data.llm_prompt_snapshot,
            "llm_output_raw": trace_data.llm_output_raw,
            "chosen_action": trace_data.chosen_action,
            "tool_arguments": trace_data.tool_arguments,
            "created_at": now
        }
        
        collection = TraceRepository._get_collection()
        collection.insert_one(trace_doc)
        
        return InferenceTrace(**trace_doc)
    
    @staticmethod
    def get_trace_by_id(trace_id: str) -> Optional[InferenceTrace]:
        """ID로 trace 조회."""
        collection = TraceRepository._get_collection()
        doc = collection.find_one({"trace_id": trace_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return InferenceTrace(**doc)
    
    @staticmethod
    def get_traces_by_npc(npc_id: str, limit: int = 100, skip: int = 0) -> List[InferenceTrace]:
        """NPC의 모든 trace 조회."""
        collection = TraceRepository._get_collection()
        docs = collection.find({"npc_id": npc_id}).sort("created_at", -1).skip(skip).limit(limit)
        
        traces = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            traces.append(InferenceTrace(**doc))
        
        return traces
    
    @staticmethod
    def get_traces_by_turn(turn_id: str) -> List[InferenceTrace]:
        """Turn의 모든 trace 조회."""
        collection = TraceRepository._get_collection()
        docs = collection.find({"turn_id": turn_id}).sort("created_at", -1)
        
        traces = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            traces.append(InferenceTrace(**doc))
        
        return traces
