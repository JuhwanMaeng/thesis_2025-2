"""Action API 엔드포인트 - NPC action 실행."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime
from app.agents.tools.schemas import Action, ActionResult
from app.schemas.trace import TraceCreate
from app.agents.tools.dispatcher import ToolDispatcher
from app.agents.tools.registry import tool_registry
from app.memory.mongo.repository.npc_repo import NPCRepository
from app.memory.mongo.repository.trace_repo import TraceRepository

router = APIRouter()


@router.post("/npc/{npc_id}/act", response_model=Dict[str, Any])
async def act(
    npc_id: str,
    observation: Dict[str, Any],
    turn_id: str = None
):
    """observation 기반 NPC action 실행."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    from app.agents.run_turn import TurnOrchestrator
    
    try:
        result = TurnOrchestrator.run_turn(npc_id, observation, turn_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")


@router.post("/npc/{npc_id}/force_action", response_model=Dict[str, Any])
async def force_action(
    npc_id: str,
    action_type: str,
    arguments: Dict[str, Any],
    observation: str = "",
    turn_id: str = None,
    reason: str = "Manually triggered action"
):
    """수동 action 실행 (프론트엔드 제어, 디버깅, 실험용)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    if not tool_registry.is_valid_tool(action_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action type: {action_type}. Valid types: {tool_registry.get_all_tool_names()}"
        )
    
    if not turn_id:
        turn_id = f"turn_{uuid.uuid4().hex[:8]}"
    
    context = {
        "npc_id": npc_id,
        "current_location": npc.current_state.get("location", "unknown"),
        "world_id": npc.world_id,
        "persona_id": npc.persona_id
    }
    
    try:
        result = ToolDispatcher.execute_raw(action_type, arguments, context)
        
        action = Action(
            action_type=action_type,
            arguments=arguments,
            reason=reason
        )
        
        trace_data = TraceCreate(
            npc_id=npc_id,
            turn_id=turn_id,
            observation=observation,
            retrieved_memories=[],
            persona_used=npc.persona_id,
            world_used=npc.world_id,
            llm_prompt_snapshot="",
            llm_output_raw="",
            chosen_action=action_type,
            tool_arguments=arguments,
            tool_execution_result=result.model_dump()
        )
        
        trace = TraceRepository.insert_trace(trace_data)
        
        return {
            "action": action.model_dump(),
            "result": result.model_dump(),
            "trace_id": trace.trace_id,
            "turn_id": turn_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")


@router.get("/tools", response_model=Dict[str, Any])
async def list_tools():
    """사용 가능한 모든 tool 목록 조회."""
    tools = tool_registry.get_all_tools()
    return {
        "tools": tools,
        "tool_names": tool_registry.get_all_tool_names(),
        "count": len(tools)
    }
