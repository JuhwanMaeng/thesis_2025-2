"""Memory API 엔드포인트."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.memory import EpisodicMemory, MemoryCreate
from app.memory.mongo.repository.memory_repo import MemoryRepository
from app.memory.mongo.repository.npc_repo import NPCRepository

router = APIRouter()


@router.post("/npc/{npc_id}/memory", response_model=EpisodicMemory, status_code=201)
async def write_memory(npc_id: str, memory_data: MemoryCreate):
    """NPC episodic memory 작성 (importance >= 0.7이면 long_term으로 자동 전환)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    memory_data_dict = memory_data.model_dump()
    memory_data_dict["npc_id"] = npc_id
    memory_data_updated = MemoryCreate(**memory_data_dict)
    
    try:
        memory = MemoryRepository.insert_memory(memory_data_updated)
        return memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write memory: {str(e)}")


@router.get("/npc/{npc_id}/memory/recent", response_model=List[EpisodicMemory])
async def get_recent_memories(
    npc_id: str,
    limit: int = Query(default=50, ge=1, le=10000),
    memory_type: Optional[str] = Query(default=None, regex="^(short_term|long_term)$")
):
    """NPC 최근 메모리 조회 (기본값: short_term만)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        if memory_type:
            memories = MemoryRepository.get_recent_memories(npc_id, limit, memory_type)
        else:
            memories = MemoryRepository.get_short_term_memories(npc_id, limit)
        
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memories: {str(e)}")


@router.get("/npc/{npc_id}/memory", response_model=List[EpisodicMemory])
async def get_all_memories(
    npc_id: str,
    limit: int = Query(default=50, ge=1, le=10000),
    memory_type: Optional[str] = Query(default=None, regex="^(short_term|long_term)$")
):
    """NPC 모든 메모리 조회."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        memories = MemoryRepository.get_recent_memories(npc_id, limit, memory_type)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memories: {str(e)}")


@router.delete("/npc/{npc_id}/memory/{memory_id}")
async def delete_memory(npc_id: str, memory_id: str):
    """Memory 삭제."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        success = MemoryRepository.delete_memory(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memory: {str(e)}")


@router.delete("/npc/{npc_id}/memory")
async def delete_memories_by_npc(
    npc_id: str,
    memory_type: Optional[str] = Query(default=None, regex="^(short_term|long_term)$")
):
    """NPC의 모든 memory 삭제 (memory_type이 지정되면 해당 타입만)."""
    npc = NPCRepository.get_npc_by_id(npc_id)
    if npc is None:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    try:
        deleted_count = MemoryRepository.delete_memories_by_npc(npc_id, memory_type)
        return {"status": "deleted", "npc_id": npc_id, "deleted_count": deleted_count, "memory_type": memory_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete memories: {str(e)}")
