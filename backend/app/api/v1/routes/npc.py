"""NPC API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.npc import NPC, NPCCreate
from app.memory.mongo.repository.npc_repo import NPCRepository

router = APIRouter()


@router.post("/npc/create", response_model=NPC, status_code=201)
async def create_npc(npc_data: NPCCreate):
    """NPC 생성."""
    try:
        npc = NPCRepository.create_npc(npc_data)
        return npc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create NPC: {str(e)}")


@router.get("/npc/{npc_id}", response_model=NPC)
async def get_npc(npc_id: str):
    """NPC 조회."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    return npc


@router.get("/npc", response_model=list[NPC])
async def list_npcs(limit: int = Query(default=100, ge=1, le=1000)):
    """NPC 목록 조회."""
    npcs = NPCRepository.list_npcs(limit=limit)
    return npcs
