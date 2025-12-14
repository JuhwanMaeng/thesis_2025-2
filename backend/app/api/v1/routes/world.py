"""World API 엔드포인트."""
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.world import WorldKnowledge, WorldCreate
from app.memory.mongo.repository.world_repo import WorldRepository
from app.memory.mongo.repository.npc_repo import NPCRepository

router = APIRouter()


@router.get("/world", response_model=List[WorldKnowledge])
async def list_worlds():
    """모든 World 목록 조회."""
    try:
        worlds = WorldRepository.list_worlds()
        return worlds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list worlds: {str(e)}")


@router.post("/world/create", response_model=WorldKnowledge, status_code=201)
async def create_world(world_data: WorldCreate):
    """World 생성."""
    try:
        world = WorldRepository.create_world(world_data)
        return world
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create world: {str(e)}")


@router.get("/world/{world_id}", response_model=WorldKnowledge)
async def get_world(world_id: str):
    """World 조회."""
    world = WorldRepository.get_world_by_id(world_id)
    
    if world is None:
        raise HTTPException(status_code=404, detail=f"World {world_id} not found")
    
    return world


@router.put("/world/{world_id}", response_model=WorldKnowledge)
async def update_world(world_id: str, update_data: dict):
    """World 업데이트."""
    try:
        world = WorldRepository.update_world(world_id, update_data)
        if world is None:
            raise HTTPException(status_code=404, detail=f"World {world_id} not found")
        return world
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update world: {str(e)}")


@router.delete("/world/{world_id}")
async def delete_world(world_id: str, delete_npcs: bool = False):
    """World 삭제. delete_npcs=True면 해당 월드의 모든 NPC도 삭제."""
    try:
        # NPC 개수 확인
        npcs = NPCRepository.get_npcs_by_world(world_id)
        npc_count = len(npcs)
        deleted_npcs = 0
        
        if npc_count > 0 and not delete_npcs:
            raise HTTPException(
                status_code=400,
                detail=f"World has {npc_count} NPC(s). Set delete_npcs=true to delete them as well."
            )
        
        # NPC 삭제 (요청된 경우)
        if delete_npcs and npc_count > 0:
            deleted_npcs = NPCRepository.delete_npcs_by_world(world_id)
        
        # World 삭제
        success = WorldRepository.delete_world(world_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"World {world_id} not found")
        
        return {
            "status": "deleted",
            "world_id": world_id,
            "deleted_npcs": deleted_npcs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete world: {str(e)}")


@router.get("/world/{world_id}/npcs", response_model=List)
async def get_world_npcs(world_id: str):
    """World에 속한 NPC 목록 조회."""
    try:
        # World 존재 확인
        world = WorldRepository.get_world_by_id(world_id)
        if world is None:
            raise HTTPException(status_code=404, detail=f"World {world_id} not found")
        
        npcs = NPCRepository.get_npcs_by_world(world_id)
        return npcs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get world NPCs: {str(e)}")
