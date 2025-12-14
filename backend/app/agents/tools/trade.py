"""Trade tool - 아이템 교환."""
from typing import Dict, Any
from app.agents.tools.base import Tool


class GiveItemTool(Tool):
    """다른 캐릭터에게 아이템을 주는 tool."""
    
    @property
    def name(self) -> str:
        return "give_item"
    
    @property
    def description(self) -> str:
        return "Give an item to another character. Use this when the NPC wants to transfer an item to someone else."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "description": "ID of the character receiving the item."
                },
                "item_id": {
                    "type": "string",
                    "description": "ID of the item being given."
                },
                "item_name": {
                    "type": "string",
                    "description": "Name of the item."
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity of items to give.",
                    "minimum": 1,
                    "default": 1
                }
            },
            "required": ["target_id", "item_id", "item_name"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Give_item action 실행."""
        target_id = arguments.get("target_id")
        item_id = arguments.get("item_id")
        item_name = arguments.get("item_name")
        quantity = arguments.get("quantity", 1)
        
        if not all([target_id, item_id, item_name]):
            return {
                "success": False,
                "action_type": "give_item",
                "effect": {},
                "error": "Missing required arguments: target_id, item_id, item_name"
            }
        
        return {
            "success": True,
            "action_type": "give_item",
            "effect": {
                "item_given": True,
                "giver": context.get("npc_id", "unknown"),
                "receiver": target_id,
                "item_id": item_id,
                "item_name": item_name,
                "quantity": quantity
            }
        }


class TradeTool(Tool):
    """다른 캐릭터와 아이템을 거래하는 tool."""
    
    @property
    def name(self) -> str:
        return "trade"
    
    @property
    def description(self) -> str:
        return "Trade items with another character. Use this when the NPC wants to exchange items with someone else."
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_id": {
                    "type": "string",
                    "description": "ID of the character to trade with."
                },
                "offer_items": {
                    "type": "array",
                    "description": "Items the NPC is offering.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "item_name": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1}
                        },
                        "required": ["item_id", "item_name"]
                    }
                },
                "request_items": {
                    "type": "array",
                    "description": "Items the NPC is requesting.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"},
                            "item_name": {"type": "string"},
                            "quantity": {"type": "integer", "minimum": 1}
                        },
                        "required": ["item_id", "item_name"]
                    }
                }
            },
            "required": ["target_id", "offer_items", "request_items"]
        }
    
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Trade action 실행."""
        target_id = arguments.get("target_id")
        offer_items = arguments.get("offer_items", [])
        request_items = arguments.get("request_items", [])
        
        if not target_id or not offer_items or not request_items:
            return {
                "success": False,
                "action_type": "trade",
                "effect": {},
                "error": "Missing required arguments: target_id, offer_items, request_items"
            }
        
        return {
            "success": True,
            "action_type": "trade",
            "effect": {
                "trade_initiated": True,
                "trader": context.get("npc_id", "unknown"),
                "trade_partner": target_id,
                "offer_items": offer_items,
                "request_items": request_items
            }
        }
