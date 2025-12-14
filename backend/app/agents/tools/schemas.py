"""Tool action 스키마."""
from typing import Dict, Any
from pydantic import BaseModel, Field


class Action(BaseModel):
    """표준 action 스키마 (LLM 출력, backend 검증, frontend 표시용)."""
    action_type: str = Field(..., description="Type of action (talk, move_to, etc.)")
    arguments: Dict[str, Any] = Field(..., description="Action-specific arguments")
    reason: str = Field(..., description="Reason for choosing this action (1-2 sentences, mandatory)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "talk",
                "arguments": {
                    "target_id": "player_001",
                    "utterance": "The ring is dangerous, you must be careful.",
                    "tone": "serious"
                },
                "reason": "Player asked about the ring, so I should warn them about its danger."
            }
        }


class ActionResult(BaseModel):
    """Tool 실행 결과."""
    success: bool = Field(..., description="Whether the action succeeded")
    action_type: str = Field(..., description="Action type that was executed")
    effect: Dict[str, Any] = Field(..., description="Effect of the action (engine-agnostic)")
    error: str = Field(default="", description="Error message if action failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "action_type": "talk",
                "effect": {
                    "spoken": True,
                    "target": "player_001",
                    "utterance": "The ring is dangerous, you must be careful."
                },
                "error": ""
            }
        }
