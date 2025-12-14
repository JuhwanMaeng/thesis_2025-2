"""Tool dispatcher - tool 실행."""
from typing import Dict, Any
from app.agents.tools.registry import tool_registry
from app.agents.tools.schemas import Action, ActionResult


class ToolDispatcher:
    """Tool 실행 디스패처."""
    
    @staticmethod
    def execute_action(action: Action, context: Dict[str, Any]) -> ActionResult:
        """Action 실행."""
        if not tool_registry.is_valid_tool(action.action_type):
            return ActionResult(
                success=False,
                action_type=action.action_type,
                effect={},
                error=f"Unknown action type: {action.action_type}"
            )
        
        tool = tool_registry.get_tool(action.action_type)
        
        try:
            result = tool.execute(action.arguments, context)
            
            return ActionResult(
                success=result.get("success", False),
                action_type=action.action_type,
                effect=result.get("effect", {}),
                error=result.get("error", "")
            )
        except Exception as e:
            return ActionResult(
                success=False,
                action_type=action.action_type,
                effect={},
                error=f"Tool execution error: {str(e)}"
            )
    
    @staticmethod
    def execute_raw(action_type: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Raw 파라미터로 action 실행 (force_action 엔드포인트용)."""
        action = Action(
            action_type=action_type,
            arguments=arguments,
            reason="Manually triggered action"
        )
        
        return ToolDispatcher.execute_action(action, context)
