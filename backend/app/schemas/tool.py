"""Dynamic tool schema."""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DynamicTool(BaseModel):
    """동적으로 추가된 도구 스키마."""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Tool name (action_type)")
    description: str = Field(..., description="Tool description for LLM")
    parameters_schema: Dict[str, Any] = Field(..., description="JSON Schema for parameters")
    code: str = Field(..., description="Python code to execute (as string)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_id": "tool_001",
                "name": "custom_action",
                "description": "A custom action that does something",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "First parameter"}
                    },
                    "required": ["param1"]
                },
                "code": "def execute(arguments, context):\n    return {'success': True, 'effect': {}}",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class DynamicToolCreate(BaseModel):
    """동적 도구 생성 스키마."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters_schema: Dict[str, Any] = Field(..., description="JSON Schema for parameters")
    code: str = Field(..., description="Python code to execute")


class DynamicToolUpdate(BaseModel):
    """동적 도구 업데이트 스키마."""
    description: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
