"""Turn API 엔드포인트 - NPC 인지 루프."""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.agents.run_turn import TurnOrchestrator

router = APIRouter()


@router.post("/npc/{npc_id}/turn", response_model=Dict[str, Any])
async def run_npc_turn(
    npc_id: str,
    observation: Dict[str, Any],
    turn_id: Optional[str] = None
):
    """NPC 턴 실행 - 전체 인지 루프."""
    try:
        result = TurnOrchestrator.run_turn(npc_id, observation, turn_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Turn execution failed: {str(e)}")
