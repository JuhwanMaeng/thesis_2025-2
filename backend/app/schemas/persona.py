"""Persona profile schema (PeaCoK-style)."""
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PersonaFactDimension(str, Enum):
    """PeaCoK dimension types for persona facts."""
    CHARACTERISTIC = "characteristic"
    ROUTINE_HABIT = "routine_habit"
    GOAL_PLAN = "goal_plan"
    EXPERIENCE = "experience"
    RELATIONSHIP = "relationship"


class PersonaFact(BaseModel):
    """Persona fact schema - individual persona knowledge facts (PeaCoK-based)."""
    fact_id: str = Field(..., description="Unique fact identifier")
    persona_id: str = Field(..., description="Persona this fact belongs to")
    npc_id: Optional[str] = Field(None, description="NPC ID if assigned to specific NPC")
    dimension: PersonaFactDimension = Field(..., description="PeaCoK dimension type")
    content: str = Field(..., description="Fact content in natural language")
    source: str = Field(default="PeaCoK", description="Source of the fact (PeaCoK, Reflection, etc.)")
    is_static: bool = Field(default=True, description="Whether this is a static (immutable) fact")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fact_id": "fact_001",
                "persona_id": "persona_001",
                "npc_id": None,
                "dimension": "characteristic",
                "content": "I am brave and never back down from a fight",
                "source": "PeaCoK",
                "is_static": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class PersonaFactCreate(BaseModel):
    """Schema for creating a persona fact."""
    persona_id: str = Field(..., description="Persona this fact belongs to")
    npc_id: Optional[str] = Field(None, description="NPC ID if assigned to specific NPC")
    dimension: PersonaFactDimension = Field(..., description="PeaCoK dimension type")
    content: str = Field(..., description="Fact content in natural language")
    source: str = Field(default="PeaCoK", description="Source of the fact")
    is_static: bool = Field(default=True, description="Whether this is a static fact")


class PersonaFactUpdate(BaseModel):
    """Schema for updating a persona fact."""
    content: Optional[str] = None
    dimension: Optional[PersonaFactDimension] = None
    is_static: Optional[bool] = None


class PersonaProfile(BaseModel):
    """Persona profile schema - static knowledge about NPC personality."""
    persona_id: str = Field(..., description="Unique persona identifier")
    name: str = Field(..., description="Persona name")
    traits: List[str] = Field(default_factory=list, description="Personality traits")
    habits: List[str] = Field(default_factory=list, description="Behavioral habits")
    goals: List[str] = Field(default_factory=list, description="Long-term goals")
    background: str = Field(default="", description="Background story")
    speech_style: str = Field(default="", description="How this persona speaks")
    relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="Relationships with other NPCs (npc_id -> relation summary)"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints: taboos, moral rules, etc."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "persona_001",
                "name": "Wise Wizard",
                "traits": ["wise", "patient", "protective"],
                "habits": ["smoking pipe", "speaking in riddles"],
                "goals": ["protect the innocent", "guide the hero"],
                "background": "An ancient wizard who has seen many ages",
                "speech_style": "Formal, uses metaphors and ancient wisdom",
                "relationships": {
                    "npc_002": "Mentor to this young hero"
                },
                "constraints": {
                    "taboos": ["killing innocents", "using dark magic"],
                    "moral_rules": ["always help those in need", "preserve balance"]
                }
            }
        }


class PersonaCreate(PersonaProfile):
    """Schema for creating a persona profile."""
    pass


class PersonaUpdate(BaseModel):
    """Schema for updating a persona profile."""
    name: Optional[str] = None
    traits: Optional[List[str]] = None
    habits: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    background: Optional[str] = None
    speech_style: Optional[str] = None
    relationships: Optional[Dict[str, str]] = None
    constraints: Optional[Dict[str, Any]] = None
