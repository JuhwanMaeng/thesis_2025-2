"""Talk tool - 언어적 상호작용."""
import logging
from typing import Dict, Any
from app.agents.tools.base import Tool

logger = logging.getLogger(__name__)


class TalkTool(Tool):
    """다른 캐릭터와 대화하는 tool."""
    
    @property
    def name(self) -> str:
        return "talk"
    
    @property
    def description(self) -> str:
        return "Speak to another character in the game world. Use this when verbal interaction is appropriate. Always provide the exact dialogue the NPC will say."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "description": "ID of the character being spoken to (e.g., player_001, npc_002)."
                },
                "utterance": {
                    "type": "string",
                    "description": "The exact dialogue spoken by the NPC. Must be a complete sentence or phrase."
                },
                "tone": {
                    "type": "string",
                    "description": "Emotional tone of the speech (e.g., calm, angry, friendly, serious, excited).",
                    "enum": ["calm", "angry", "friendly", "serious", "excited", "worried", "neutral"]
                }
            },
            "required": ["target_id", "utterance"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Talk action 실행."""
        try:
            target_id = arguments.get("target_id")
            utterance = arguments.get("utterance")
            tone = arguments.get("tone", "neutral")
            
            if not target_id or not utterance:
                error_msg = f"Missing required arguments: target_id={target_id}, utterance={utterance}"
                logger.error(f"TalkTool failed: {error_msg}")
                return {
                    "success": False,
                    "action_type": "talk",
                    "effect": {},
                    "error": error_msg
                }
            
            result = {
                "success": True,
                "action_type": "talk",
                "effect": {
                    "spoken": True,
                    "target": target_id,
                    "utterance": str(utterance),
                    "tone": str(tone),
                    "speaker": context.get("npc_id", "unknown")
                }
            }
            
            return result
            
        except Exception as e:
            error_msg = f"TalkTool execution exception: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "action_type": "talk",
                "effect": {},
                "error": error_msg
            }
