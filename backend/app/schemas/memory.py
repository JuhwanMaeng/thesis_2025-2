"""Episodic memory schema."""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# Constant for long-term memory threshold
LONG_TERM_THRESHOLD = 0.7


class MemorySource(str):
    """Memory source types."""
    OBSERVATION = "observation"
    ACTION = "action"
    REFLECTION = "reflection"


class MemoryType(str):
    """Memory type."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class EpisodicMemory(BaseModel):
    """Episodic memory schema - stores both short-term and long-term memories."""
    memory_id: str = Field(..., description="Unique memory identifier")
    npc_id: str = Field(..., description="NPC who owns this memory")
    memory_type: Literal["short_term", "long_term"] = Field(
        ...,
        description="Type of memory: short_term (raw log) or long_term (curated)"
    )
    content: str = Field(..., description="Memory content: raw observation/action/reflection text")
    source: Literal["observation", "action", "reflection"] = Field(
        ...,
        description="Source of memory: observation, action, or reflection"
    )
    importance: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Importance score (0.0-1.0). >= 0.7 converts to long_term"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    linked_entities: List[str] = Field(
        default_factory=list,
        description="Linked entity IDs (other NPCs, locations, items)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "memory_id": "mem_001",
                "npc_id": "npc_001",
                "memory_type": "short_term",
                "content": "Player approached and asked about the ring",
                "source": "observation",
                "importance": 0.5,
                "tags": ["player_interaction", "ring"],
                "linked_entities": ["player_001"],
                "created_at": "2024-01-01T00:00:00"
            }
        }


class MemoryCreate(BaseModel):
    """Schema for creating a memory."""
    npc_id: str = Field(..., description="NPC who owns this memory")
    content: str = Field(..., description="Memory content")
    source: Literal["observation", "action", "reflection"] = Field(
        default="observation",
        description="Source of memory"
    )
    importance: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Importance score. If >= 0.7, will be converted to long_term"
    )
    tags: List[str] = Field(default_factory=list, description="Tags")
    linked_entities: List[str] = Field(default_factory=list, description="Linked entities")
