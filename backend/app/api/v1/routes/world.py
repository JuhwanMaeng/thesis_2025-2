"""World API 엔드포인트."""
from fastapi import APIRouter, HTTPException
from app.schemas.world import WorldKnowledge, WorldCreate
from app.memory.mongo.repository.world_repo import WorldRepository

router = APIRouter()


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
