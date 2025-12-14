"""NPC repository - CRUD 작업만."""
from typing import Optional
from datetime import datetime
import uuid
from app.memory.mongo.client import get_collection
from app.schemas.npc import NPC, NPCCreate


class NPCRepository:
    """NPC 작업 repository."""
    
    @staticmethod
    def _get_collection():
        return get_collection("npcs")
    
    @staticmethod
    def create_npc(npc_data: NPCCreate) -> NPC:
        """NPC 생성."""
        npc_id = f"npc_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        npc_doc = {
            "npc_id": npc_id,
            "name": npc_data.name,
            "role": npc_data.role,
            "persona_id": npc_data.persona_id,
            "world_id": npc_data.world_id,
            "current_state": npc_data.current_state,
            "created_at": now,
            "updated_at": now
        }
        
        collection = NPCRepository._get_collection()
        collection.insert_one(npc_doc)
        
        return NPC(**npc_doc)
    
    @staticmethod
    def get_npc_by_id(npc_id: str) -> Optional[NPC]:
        """ID로 NPC 조회."""
        collection = NPCRepository._get_collection()
        doc = collection.find_one({"npc_id": npc_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return NPC(**doc)
    
    @staticmethod
    def update_npc_state(npc_id: str, new_state: dict) -> Optional[NPC]:
        """NPC current_state 업데이트."""
        collection = NPCRepository._get_collection()
        result = collection.update_one(
            {"npc_id": npc_id},
            {
                "$set": {
                    "current_state": new_state,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return None
        
        return NPCRepository.get_npc_by_id(npc_id)
    
    @staticmethod
    def list_npcs(limit: int = 100) -> list[NPC]:
        """모든 NPC 목록 조회."""
        collection = NPCRepository._get_collection()
        docs = collection.find().limit(limit)
        
        npcs = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            npcs.append(NPC(**doc))
        
        return npcs
