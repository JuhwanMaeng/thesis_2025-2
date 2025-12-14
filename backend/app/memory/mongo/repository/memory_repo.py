"""Memory repository - importance 기반 전환 포함 CRUD 작업."""
from typing import List, Optional
from datetime import datetime
import uuid
from app.memory.mongo.client import get_collection
from app.schemas.memory import EpisodicMemory, MemoryCreate, LONG_TERM_THRESHOLD


class MemoryRepository:
    """Episodic memory 작업 repository."""
    
    @staticmethod
    def _get_collection():
        return get_collection("episodic_memory")
    
    @staticmethod
    def insert_memory(memory_data: MemoryCreate, importance_threshold: float = None) -> EpisodicMemory:
        """Memory 삽입 (importance >= threshold면 long_term으로 자동 전환)."""
        memory_id = f"mem_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        
        # threshold가 제공되면 사용, 아니면 기본값 사용
        threshold = importance_threshold if importance_threshold is not None else LONG_TERM_THRESHOLD
        memory_type = "long_term" if memory_data.importance >= threshold else "short_term"
        
        memory_doc = {
            "memory_id": memory_id,
            "npc_id": memory_data.npc_id,
            "memory_type": memory_type,
            "content": memory_data.content,
            "source": memory_data.source,
            "importance": memory_data.importance,
            "tags": memory_data.tags,
            "linked_entities": memory_data.linked_entities,
            "created_at": now
        }
        
        collection = MemoryRepository._get_collection()
        collection.insert_one(memory_doc)
        
        if memory_type == "long_term":
            try:
                from app.memory.vector.vectorizer import Vectorizer
                vectorizer = Vectorizer('episodic')
                vectorizer.vectorize_episodic_memory(
                    memory_id=memory_id,
                    npc_id=memory_data.npc_id,
                    content=memory_data.content,
                    importance=memory_data.importance,
                    created_at=now.isoformat()
                )
            except Exception as e:
                import logging
                logging.warning(f"Failed to vectorize memory {memory_id}: {str(e)}")
        
        return EpisodicMemory(**memory_doc)
    
    @staticmethod
    def get_memory_by_id(memory_id: str) -> Optional[EpisodicMemory]:
        """ID로 memory 조회."""
        collection = MemoryRepository._get_collection()
        doc = collection.find_one({"memory_id": memory_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return EpisodicMemory(**doc)
    
    @staticmethod
    def get_recent_memories(npc_id: str, limit: int = 50, memory_type: Optional[str] = None) -> List[EpisodicMemory]:
        """NPC 최근 memory 조회 (memory_type이 None이면 모두 반환)."""
        collection = MemoryRepository._get_collection()
        
        query = {"npc_id": npc_id}
        if memory_type:
            query["memory_type"] = memory_type
        
        docs = collection.find(query).sort("created_at", -1).limit(limit)
        
        memories = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            memories.append(EpisodicMemory(**doc))
        
        return memories
    
    @staticmethod
    def get_short_term_memories(npc_id: str, limit: int = 50) -> List[EpisodicMemory]:
        """최근 short-term memory만 조회."""
        return MemoryRepository.get_recent_memories(npc_id, limit, memory_type="short_term")
    
    @staticmethod
    def get_long_term_memories(npc_id: str, limit: int = 50) -> List[EpisodicMemory]:
        """최근 long-term memory만 조회."""
        return MemoryRepository.get_recent_memories(npc_id, limit, memory_type="long_term")
    
    @staticmethod
    def convert_to_long_term(memory_id: str) -> Optional[EpisodicMemory]:
        """Memory를 수동으로 long-term으로 전환."""
        collection = MemoryRepository._get_collection()
        result = collection.update_one(
            {"memory_id": memory_id},
            {"$set": {"memory_type": "long_term"}}
        )
        
        if result.matched_count == 0:
            return None
        
        return MemoryRepository.get_memory_by_id(memory_id)
    
    @staticmethod
    def delete_memory(memory_id: str) -> bool:
        """Memory 삭제."""
        collection = MemoryRepository._get_collection()
        result = collection.delete_one({"memory_id": memory_id})
        return result.deleted_count > 0
    
    @staticmethod
    def delete_memories_by_npc(npc_id: str, memory_type: Optional[str] = None) -> int:
        """NPC의 모든 memory 삭제 (memory_type이 지정되면 해당 타입만)."""
        collection = MemoryRepository._get_collection()
        query = {"npc_id": npc_id}
        if memory_type:
            query["memory_type"] = memory_type
        result = collection.delete_many(query)
        return result.deleted_count
