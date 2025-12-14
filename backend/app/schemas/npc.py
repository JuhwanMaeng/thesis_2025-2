"""NPC core schema."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


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
