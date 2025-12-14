"""Quest tools - 퀘스트 시작 및 업데이트."""
from typing import Dict, Any
from app.agents.tools.base import Tool


class StartQuestTool(Tool):
    """퀘스트를 시작하는 tool."""
    
    @property
    def name(self) -> str:
        return "start_quest"
    
    @property
    def description(self) -> str:
        return "Start a new quest for a target character. Use this when the NPC wants to assign a quest or task to another character."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "description": "ID of the character receiving the quest."
                },
                "quest_id": {
                    "type": "string",
                    "description": "Unique identifier for the quest."
                },
                "quest_name": {
                    "type": "string",
                    "description": "Name of the quest."
                },
                "quest_description": {
                    "type": "string",
                    "description": "Description of what needs to be done."
                },
                "reward": {
                    "type": "string",
                    "description": "Reward for completing the quest (optional)."
                }
            },
            "required": ["target_id", "quest_id", "quest_name", "quest_description"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Start_quest action 실행."""
        target_id = arguments.get("target_id")
        quest_id = arguments.get("quest_id")
        quest_name = arguments.get("quest_name")
        quest_description = arguments.get("quest_description")
        
        if not all([target_id, quest_id, quest_name, quest_description]):
            return {
                "success": False,
                "action_type": "start_quest",
                "effect": {},
                "error": "Missing required arguments: target_id, quest_id, quest_name, quest_description"
            }
        
        return {
            "success": True,
            "action_type": "start_quest",
            "effect": {
                "quest_started": True,
                "quest_id": quest_id,
                "quest_name": quest_name,
                "quest_giver": context.get("npc_id", "unknown"),
                "quest_receiver": target_id,
                "quest_description": quest_description,
                "reward": arguments.get("reward", "")
            }
        }


class UpdateQuestTool(Tool):
    """퀘스트 진행 상황을 업데이트하는 tool."""
    
    @property
    def name(self) -> str:
        return "update_quest"
    
    @property
    def description(self) -> str:
        return "Update the progress or status of an existing quest. Use this when quest objectives are completed or quest status changes."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "quest_id": {
                    "type": "string",
                    "description": "ID of the quest to update."
                },
                "status": {
                    "type": "string",
                    "description": "New status of the quest.",
                    "enum": ["in_progress", "completed", "failed", "cancelled"]
                },
                "progress_note": {
                    "type": "string",
                    "description": "Note about quest progress (optional)."
                }
            },
            "required": ["quest_id", "status"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update_quest action 실행."""
        quest_id = arguments.get("quest_id")
        status = arguments.get("status")
        
        if not quest_id or not status:
            return {
                "success": False,
                "action_type": "update_quest",
                "effect": {},
                "error": "Missing required arguments: quest_id and status"
            }
        
        return {
            "success": True,
            "action_type": "update_quest",
            "effect": {
                "quest_updated": True,
                "quest_id": quest_id,
                "new_status": status,
                "updated_by": context.get("npc_id", "unknown"),
                "progress_note": arguments.get("progress_note", "")
            }
        }
