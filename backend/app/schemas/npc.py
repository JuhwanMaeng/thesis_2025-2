"""NPC core schema."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class NPCConfig(BaseModel):
    """NPC별 설정 파라미터."""
    retrieval_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="각 인덱스당 검색할 메모리 개수"
    )
    importance_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="장기 기억 전환 임계값"
    )
    reflection_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Reflection 트리거 임계값"
    )
    max_facts_per_dimension: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Dimension당 최대 fact 개수"
    )


class NPCBase(BaseModel):
    """Base NPC schema."""
    name: str = Field(..., description="NPC name")
    role: str = Field(..., description="NPC role in the world")
    persona_id: str = Field(..., description="Reference to persona profile")
    world_id: str = Field(..., description="Reference to world knowledge")
    current_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mutable current state (emotion, goal, location, hp, status flags)"
    )
    config: Optional[NPCConfig] = Field(
        default_factory=NPCConfig,
        description="NPC별 설정 파라미터"
    )


class NPCCreate(NPCBase):
    """Schema for creating an NPC."""
    pass


class NPC(NPCBase):
    """Full NPC schema with metadata."""
    npc_id: str = Field(..., description="Unique NPC identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "npc_id": "npc_001",
                "name": "Gandalf",
                "role": "Wizard",
                "persona_id": "persona_001",
                "world_id": "world_001",
                "current_state": {
                    "emotion": "calm",
                    "goal": "protect_the_ring",
                    "location": "shire",
                    "hp": 100,
                    "status_flags": ["magic_ready", "alert"]
                },
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
