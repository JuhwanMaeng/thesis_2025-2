"""Combat tools - 공격 및 방어."""
from typing import Dict, Any
from app.agents.tools.base import Tool


class AttackTool(Tool):
    """다른 캐릭터를 공격하는 tool."""
    
    @property
    def name(self) -> str:
        return "attack"
    
    @property
    def description(self) -> str:
        return "Attack another character. Use this when combat is necessary and appropriate. Only use in combat situations."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "description": "ID of the character being attacked."
                },
                "attack_type": {
                    "type": "string",
                    "description": "Type of attack (e.g., melee, ranged, magic).",
                    "enum": ["melee", "ranged", "magic"]
                },
                "intensity": {
                    "type": "string",
                    "description": "Intensity of the attack.",
                    "enum": ["light", "medium", "heavy"]
                }
            },
            "required": ["target_id", "attack_type"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Attack action 실행."""
        target_id = arguments.get("target_id")
        attack_type = arguments.get("attack_type")
        intensity = arguments.get("intensity", "medium")
        
        if not target_id or not attack_type:
            return {
                "success": False,
                "action_type": "attack",
                "effect": {},
                "error": "Missing required arguments: target_id and attack_type"
            }
        
        return {
            "success": True,
            "action_type": "attack",
            "effect": {
                "attacked": True,
                "attacker": context.get("npc_id", "unknown"),
                "target": target_id,
                "attack_type": attack_type,
                "intensity": intensity
            }
        }


class DefendTool(Tool):
    """공격에 방어하는 tool."""
    
    @property
    def name(self) -> str:
        return "defend"
    
    @property
    def description(self) -> str:
        return "Defend against incoming attacks. Use this when the NPC is under attack and needs to protect themselves."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "defense_type": {
                    "type": "string",
                    "description": "Type of defense (e.g., block, dodge, shield).",
                    "enum": ["block", "dodge", "shield", "parry"]
                },
                "intensity": {
                    "type": "string",
                    "description": "Intensity of the defense.",
                    "enum": ["light", "medium", "heavy"]
                }
            },
            "required": ["defense_type"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Defend action 실행."""
        defense_type = arguments.get("defense_type")
        intensity = arguments.get("intensity", "medium")
        
        if not defense_type:
            return {
                "success": False,
                "action_type": "defend",
                "effect": {},
                "error": "Missing required argument: defense_type"
            }
        
        return {
            "success": True,
            "action_type": "defend",
            "effect": {
                "defended": True,
                "defender": context.get("npc_id", "unknown"),
                "defense_type": defense_type,
                "intensity": intensity
            }
        }
