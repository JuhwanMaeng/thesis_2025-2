"""World knowledge schema."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class WorldKnowledge(BaseModel):
    """World knowledge schema - static knowledge about the game world."""
    world_id: str = Field(..., description="Unique world identifier")
    title: str = Field(..., description="World title")
    rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="World rules: laws, factions, social norms"
    )
    locations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Location information"
    )
    danger_levels: Dict[str, float] = Field(
        default_factory=dict,
        description="Danger levels by location or region"
    )
    global_constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global constraints that affect all NPCs"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "world_id": "world_001",
                "title": "Middle Earth",
                "rules": {
                    "laws": ["No magic in public", "Respect the king"],
                    "factions": {
                        "wizards": "Neutral, protect balance",
                        "dark_lords": "Evil, seek power"
                    },
                    "social_norms": ["Greet with respect", "Offer help to travelers"]
                },
                "locations": {
                    "shire": {"type": "peaceful", "population": "hobbits"},
                    "mordor": {"type": "dangerous", "population": "orcs"}
                },
                "danger_levels": {
                    "shire": 0.1,
                    "mordor": 0.9
                },
                "global_constraints": {
                    "magic_available": True,
                    "time_period": "medieval"
                }
            }
        }


class WorldCreate(WorldKnowledge):
    """Schema for creating world knowledge."""
    pass
