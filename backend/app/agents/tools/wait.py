"""Wait tool - 행동 없음."""
from typing import Dict, Any
from app.agents.tools.base import Tool


class WaitTool(Tool):
    """대기하는 tool (행동 없음)."""
    
    @property
    def name(self) -> str:
        return "wait"
    
    @property
    def description(self) -> str:
        return "Wait and do nothing. Use this when the NPC should not take any action in this turn, or when waiting is the appropriate response."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Reason for waiting (optional, for logging)."
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Wait action 실행."""
        return {
            "success": True,
            "action_type": "wait",
            "effect": {
                "waited": True,
                "npc_id": context.get("npc_id", "unknown"),
                "reason": arguments.get("reason", "No action needed")
            }
        }
