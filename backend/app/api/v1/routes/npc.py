"""NPC API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from app.schemas.npc import NPC, NPCCreate, NPCConfig
from app.memory.mongo.repository.npc_repo import NPCRepository
from app.services.npc_generator import NPCGenerator

router = APIRouter()


@router.post("/npc/create", response_model=NPC, status_code=201)
async def create_npc(npc_data: NPCCreate):
    """NPC 생성."""
    try:
        npc = NPCRepository.create_npc(npc_data)
        return npc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create NPC: {str(e)}")


@router.post("/npc/generate", response_model=Dict[str, Any], status_code=201)
async def generate_npc(
    description: str = Body(..., embed=True, description="NPC에 대한 간단한 설명"),
    role: Optional[str] = Body(None, embed=True, description="NPC 역할 (선택사항)"),
    config: Optional[NPCConfig] = Body(None, embed=True, description="NPC 설정 (선택사항)")
):
    """LLM을 사용하여 NPC 자동 생성."""
    try:
        result = NPCGenerator.create_npc_from_description(description, role, config)
        return {
            "npc": result["npc"].model_dump() if hasattr(result["npc"], 'model_dump') else result["npc"].dict(),
            "persona": result["persona"].model_dump() if hasattr(result["persona"], 'model_dump') else result["persona"].dict(),
            "world": result["world"].model_dump() if hasattr(result["world"], 'model_dump') else result["world"].dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate NPC: {str(e)}")


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


@router.put("/npc/{npc_id}", response_model=NPC)
async def update_npc(npc_id: str, updates: Dict[str, Any] = Body(...)):
    """NPC 업데이트 (config, current_state 등)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        updated_npc = NPCRepository.update_npc(npc_id, updates)
        if updated_npc is None:
            raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
        return updated_npc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update NPC: {str(e)}")


@router.put("/npc/{npc_id}/config", response_model=NPC)
async def update_npc_config(npc_id: str, config: NPCConfig):
    """NPC config 업데이트."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        config_dict = config.model_dump() if hasattr(config, 'model_dump') else config.dict()
        updated_npc = NPCRepository.update_npc_config(npc_id, config_dict)
        if updated_npc is None:
            raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
        return updated_npc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update NPC config: {str(e)}")


@router.delete("/npc/{npc_id}")
async def delete_npc(npc_id: str):
    """NPC 삭제."""
    try:
        success = NPCRepository.delete_npc(npc_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
        return {"status": "deleted", "npc_id": npc_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete NPC: {str(e)}")
