"""World repository - CRUD 작업만."""
from typing import Optional
import uuid
from app.memory.mongo.client import get_collection
from app.schemas.world import WorldKnowledge, WorldCreate


class WorldRepository:
    """World knowledge 작업 repository."""
    
    @staticmethod
    def _get_collection():
        return get_collection("world_knowledge")
    
    @staticmethod
    def create_world(world_data: WorldCreate) -> WorldKnowledge:
        """World knowledge 생성."""
        world_id = world_data.world_id or f"world_{uuid.uuid4().hex[:8]}"
        
        world_doc = {
            "world_id": world_id,
            "title": world_data.title,
            "rules": world_data.rules,
            "locations": world_data.locations,
            "danger_levels": world_data.danger_levels,
            "global_constraints": world_data.global_constraints
        }
        
        collection = WorldRepository._get_collection()
        collection.insert_one(world_doc)
        
        return WorldKnowledge(**world_doc)
    
    @staticmethod
    def get_world_by_id(world_id: str) -> Optional[WorldKnowledge]:
        """ID로 world 조회."""
        collection = WorldRepository._get_collection()
        doc = collection.find_one({"world_id": world_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return WorldKnowledge(**doc)
    
    @staticmethod
    def list_worlds(limit: int = 100) -> list[WorldKnowledge]:
        """모든 World 목록 조회."""
        collection = WorldRepository._get_collection()
        docs = collection.find().limit(limit)
        
        worlds = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            worlds.append(WorldKnowledge(**doc))
        
        return worlds
    
    @staticmethod
    def update_world(world_id: str, update_data: dict) -> Optional[WorldKnowledge]:
        """World knowledge 업데이트."""
        collection = WorldRepository._get_collection()
        result = collection.update_one(
            {"world_id": world_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return WorldRepository.get_world_by_id(world_id)
    
    @staticmethod
    def delete_world(world_id: str) -> bool:
        """World 삭제."""
        collection = WorldRepository._get_collection()
        result = collection.delete_one({"world_id": world_id})
        return result.deleted_count > 0
