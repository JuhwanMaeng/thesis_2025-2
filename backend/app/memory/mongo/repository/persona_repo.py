"""Persona repository - CRUD 작업만."""
from typing import Optional, List
import uuid
from datetime import datetime
from app.memory.mongo.client import get_collection
from app.schemas.persona import (
    PersonaProfile, PersonaCreate,
    PersonaFact, PersonaFactCreate, PersonaFactUpdate, PersonaFactDimension
)


class PersonaRepository:
    """Persona profile 작업 repository."""
    
    @staticmethod
    def _get_collection():
        return get_collection("persona_profiles")
    
    @staticmethod
    def create_persona(persona_data: PersonaCreate) -> PersonaProfile:
        """Persona profile 생성."""
        persona_id = persona_data.persona_id or f"persona_{uuid.uuid4().hex[:8]}"
        
        persona_doc = {
            "persona_id": persona_id,
            "name": persona_data.name,
            "traits": persona_data.traits,
            "habits": persona_data.habits,
            "goals": persona_data.goals,
            "background": persona_data.background,
            "speech_style": persona_data.speech_style,
            "relationships": persona_data.relationships,
            "constraints": persona_data.constraints
        }
        
        collection = PersonaRepository._get_collection()
        collection.insert_one(persona_doc)
        
        return PersonaProfile(**persona_doc)
    
    @staticmethod
    def get_persona_by_id(persona_id: str) -> Optional[PersonaProfile]:
        """ID로 persona 조회."""
        collection = PersonaRepository._get_collection()
        doc = collection.find_one({"persona_id": persona_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        return PersonaProfile(**doc)
    
    @staticmethod
    def update_persona(persona_id: str, update_data: dict) -> Optional[PersonaProfile]:
        """Persona profile 업데이트."""
        collection = PersonaRepository._get_collection()
        result = collection.update_one(
            {"persona_id": persona_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return PersonaRepository.get_persona_by_id(persona_id)


class PersonaFactRepository:
    """Persona fact repository - CRUD for PersonaFact."""
    
    @staticmethod
    def _get_collection():
        return get_collection("persona_facts")
    
    @staticmethod
    def create_fact(fact_data: PersonaFactCreate) -> PersonaFact:
        """Persona fact 생성."""
        fact_id = f"fact_{uuid.uuid4().hex[:8]}"
        
        fact_doc = {
            "fact_id": fact_id,
            "persona_id": fact_data.persona_id,
            "npc_id": fact_data.npc_id,
            "dimension": fact_data.dimension.value,
            "content": fact_data.content,
            "source": fact_data.source,
            "is_static": fact_data.is_static,
            "created_at": datetime.utcnow()
        }
        
        collection = PersonaFactRepository._get_collection()
        collection.insert_one(fact_doc)
        
        return PersonaFact(**fact_doc)
    
    @staticmethod
    def create_facts_bulk(facts_data: List[PersonaFactCreate]) -> List[PersonaFact]:
        """여러 persona facts를 한 번에 생성."""
        fact_docs = []
        for fact_data in facts_data:
            fact_id = f"fact_{uuid.uuid4().hex[:8]}"
            fact_docs.append({
                "fact_id": fact_id,
                "persona_id": fact_data.persona_id,
                "npc_id": fact_data.npc_id,
                "dimension": fact_data.dimension.value,
                "content": fact_data.content,
                "source": fact_data.source,
                "is_static": fact_data.is_static,
                "created_at": datetime.utcnow()
            })
        
        collection = PersonaFactRepository._get_collection()
        if fact_docs:
            collection.insert_many(fact_docs)
        
        return [PersonaFact(**doc) for doc in fact_docs]
    
    @staticmethod
    def get_fact_by_id(fact_id: str) -> Optional[PersonaFact]:
        """ID로 fact 조회."""
        collection = PersonaFactRepository._get_collection()
        doc = collection.find_one({"fact_id": fact_id})
        
        if doc is None:
            return None
        
        if "_id" in doc:
            del doc["_id"]
        
        # dimension을 enum으로 변환
        if isinstance(doc.get("dimension"), str):
            try:
                doc["dimension"] = PersonaFactDimension(doc["dimension"])
            except ValueError:
                pass
        
        return PersonaFact(**doc)
    
    @staticmethod
    def get_facts_by_persona(persona_id: str, dimension: Optional[PersonaFactDimension] = None) -> List[PersonaFact]:
        """Persona ID로 facts 조회."""
        collection = PersonaFactRepository._get_collection()
        query = {"persona_id": persona_id}
        
        if dimension:
            query["dimension"] = dimension.value
        
        docs = list(collection.find(query))
        
        facts = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            
            # dimension을 enum으로 변환
            if isinstance(doc.get("dimension"), str):
                try:
                    doc["dimension"] = PersonaFactDimension(doc["dimension"])
                except ValueError:
                    continue
            
            facts.append(PersonaFact(**doc))
        
        return facts
    
    @staticmethod
    def get_facts_by_npc(npc_id: str, dimension: Optional[PersonaFactDimension] = None) -> List[PersonaFact]:
        """NPC ID로 facts 조회."""
        collection = PersonaFactRepository._get_collection()
        query = {"npc_id": npc_id}
        
        if dimension:
            query["dimension"] = dimension.value
        
        docs = list(collection.find(query))
        
        facts = []
        for doc in docs:
            if "_id" in doc:
                del doc["_id"]
            
            # dimension을 enum으로 변환
            if isinstance(doc.get("dimension"), str):
                try:
                    doc["dimension"] = PersonaFactDimension(doc["dimension"])
                except ValueError:
                    continue
            
            facts.append(PersonaFact(**doc))
        
        return facts
    
    @staticmethod
    def update_fact(fact_id: str, update_data: PersonaFactUpdate) -> Optional[PersonaFact]:
        """Persona fact 업데이트."""
        collection = PersonaFactRepository._get_collection()
        
        update_dict = {}
        if update_data.content is not None:
            update_dict["content"] = update_data.content
        if update_data.dimension is not None:
            update_dict["dimension"] = update_data.dimension.value
        if update_data.is_static is not None:
            update_dict["is_static"] = update_data.is_static
        
        if not update_dict:
            return PersonaFactRepository.get_fact_by_id(fact_id)
        
        result = collection.update_one(
            {"fact_id": fact_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            return None
        
        return PersonaFactRepository.get_fact_by_id(fact_id)
    
    @staticmethod
    def delete_fact(fact_id: str) -> bool:
        """Persona fact 삭제."""
        collection = PersonaFactRepository._get_collection()
        result = collection.delete_one({"fact_id": fact_id})
        return result.deleted_count > 0
    
    @staticmethod
    def count_facts_by_persona(persona_id: str) -> int:
        """Persona의 fact 개수 조회."""
        collection = PersonaFactRepository._get_collection()
        return collection.count_documents({"persona_id": persona_id})
