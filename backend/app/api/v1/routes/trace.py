"""Inference trace API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.trace import InferenceTrace
from app.memory.mongo.repository.trace_repo import TraceRepository

router = APIRouter()


@router.get("/npc/{npc_id}/traces", response_model=List[InferenceTrace])
async def get_traces(
    npc_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """NPC inference trace 목록 조회."""
    try:
        traces = TraceRepository.get_traces_by_npc(npc_id, limit=limit, skip=offset)
        return traces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get traces: {str(e)}")


@router.get("/trace/{trace_id}", response_model=InferenceTrace)
async def get_trace(trace_id: str):
    """Inference trace 조회."""
    trace = TraceRepository.get_trace_by_id(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
    
    return trace
