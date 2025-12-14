"""Move tool - 위치 이동."""
from typing import Dict, Any
from app.agents.tools.base import Tool


class MoveToTool(Tool):
    """위치로 이동하는 tool."""
    
    @property
    def name(self) -> str:
        return "move_to"
    
    @property
    def description(self) -> str:
        return "Move to a specific location in the game world. Use this when the NPC needs to change location."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location_id": {
                    "type": "string",
                    "description": "ID of the destination location (e.g., town_square, forest_entrance)."
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for moving to this location (optional, for logging)."
                }
            },
            "required": ["location_id"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Move_to action 실행."""
        location_id = arguments.get("location_id")
        
        if not location_id:
            return {
                "success": False,
                "action_type": "move_to",
                "effect": {},
                "error": "Missing required argument: location_id"
            }
        
        return {
            "success": True,
            "action_type": "move_to",
            "effect": {
                "moved": True,
                "from_location": context.get("current_location", "unknown"),
                "to_location": location_id,
                "npc_id": context.get("npc_id", "unknown")
            }
        }
