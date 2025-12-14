"""Inference trace schema - mandatory for thesis debugging."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InferenceTrace(BaseModel):
    """Inference trace schema - tracks every LLM decision for debugging."""
    trace_id: str = Field(..., description="Unique trace identifier")
    npc_id: str = Field(..., description="NPC who made this decision")
    turn_id: str = Field(..., description="Turn identifier")
    observation: str = Field(default="", description="What the NPC observed")
    retrieved_memories: List[str] = Field(
        default_factory=list,
        description="Memory IDs that were retrieved (source IDs, not vector IDs)"
    )
    retrieval_query_text: str = Field(
        default="",
        description="Query text used for vector retrieval"
    )
    retrieval_indices_searched: List[str] = Field(
        default_factory=list,
        description="Vector indices that were searched (episodic, persona, world)"
    )
    retrieval_vector_ids: List[int] = Field(
        default_factory=list,
        description="Vector IDs that were retrieved from FAISS"
    )
    retrieval_similarity_scores: List[float] = Field(
        default_factory=list,
        description="Similarity scores for retrieved vectors"
    )
    persona_used: Optional[str] = Field(
        default=None,
        description="Persona ID that was used"
    )
    world_used: Optional[str] = Field(
        default=None,
        description="World ID that was used"
    )
    llm_prompt_snapshot: str = Field(
        default="",
        description="Full prompt sent to LLM (for debugging)"
    )
    llm_output_raw: str = Field(
        default="",
        description="Raw LLM output"
    )
    chosen_action: str = Field(
        default="",
        description="Action that was chosen"
    )
    tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool"
    )
    tool_execution_result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Result of tool execution (success, effect, error)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "trace_001",
                "npc_id": "npc_001",
                "turn_id": "turn_001",
                "observation": "Player asked about the ring",
                "retrieved_memories": ["mem_001", "mem_002"],
                "persona_used": "persona_001",
                "world_used": "world_001",
                "llm_prompt_snapshot": "You are Gandalf...",
                "llm_output_raw": "I should warn the player...",
                "chosen_action": "Talk",
                "tool_arguments": {"message": "The ring is dangerous"},
                "created_at": "2024-01-01T00:00:00"
            }
        }


class TraceCreate(BaseModel):
    """Schema for creating an inference trace."""
    npc_id: str = Field(..., description="NPC ID")
    turn_id: str = Field(..., description="Turn ID")
    observation: str = Field(default="", description="Observation")
    retrieved_memories: List[str] = Field(default_factory=list)
    retrieval_query_text: str = Field(default="")
    retrieval_indices_searched: List[str] = Field(default_factory=list)
    retrieval_vector_ids: List[int] = Field(default_factory=list)
    retrieval_similarity_scores: List[float] = Field(default_factory=list)
    persona_used: Optional[str] = None
    world_used: Optional[str] = None
    llm_prompt_snapshot: str = Field(default="")
    llm_output_raw: str = Field(default="")
    chosen_action: str = Field(default="")
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    tool_execution_result: Dict[str, Any] = Field(default_factory=dict)
