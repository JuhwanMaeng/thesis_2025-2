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
        
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            result = tool.execute(action.arguments, context)
            
            # result가 딕셔너리인지 확인
            if not isinstance(result, dict):
                error_msg = f"Tool returned invalid result type: {type(result)}"
                logger.error(f"Tool {action.action_type} - {error_msg}")
                return ActionResult(
                    success=False,
                    action_type=action.action_type,
                    effect={},
                    error=error_msg
                )
            
            success = result.get("success", False)
            effect = result.get("effect", {})
            error = result.get("error", "")
            
            # success가 False인 경우 에러 메시지 확실히 설정
            if not success:
                if not error:
                    error = f"Tool {action.action_type} execution failed without error message. Result: {result}"
                    logger.error(f"Tool {action.action_type} failed without error message. Result: {result}")
                else:
                    logger.error(f"Tool {action.action_type} failed: {error}. Arguments: {action.arguments}")
            
            action_result = ActionResult(
                success=success,
                action_type=action.action_type,
                effect=effect or {},
                error=error
            )
            
            return action_result
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Tool execution error for {action.action_type}: {str(e)}", exc_info=True)
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
