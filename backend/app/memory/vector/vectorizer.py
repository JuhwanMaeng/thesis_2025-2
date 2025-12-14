"""다양한 source type에 대한 vectorization 파이프라인."""
import json
import numpy as np
from typing import List, Dict, Any, Optional
from app.services.embedding_service import embedding_service
from app.memory.vector.faiss_manager import FAISSManager
from app.memory.vector.metadata_store import MetadataStore
from app.core.config import settings


class Vectorizer:
    """다양한 source type의 vectorization 처리."""
    
    def __init__(self, index_name: str):
        """특정 index용 vectorizer 초기화."""
        self.index_name = index_name
        self.faiss_manager = FAISSManager(index_name, settings.openai_embedding_dim)
        self.metadata_store = MetadataStore(index_name)
        
        if self.faiss_manager.load_index():
            self.metadata_store.load()
    
    def vectorize_episodic_memory(self, memory_id: str, npc_id: str, content: str, 
                                   importance: float, created_at: str) -> int:
        """Long-term episodic memory vectorization."""
        if self.faiss_manager.index is None:
            self.faiss_manager.create_index()
        
        embedding = embedding_service.embed_single(content)
        vector_ids = self.faiss_manager.add_vectors(embedding)
        vector_id = vector_ids[0]
        
        metadata = {
            'source_type': 'episodic',
            'source_id': memory_id,
            'npc_id': npc_id,
            'importance': importance,
            'created_at': created_at,
            'summary': content[:200]
        }
        self.metadata_store.add(metadata)
        
        self.faiss_manager.save_index()
        self.metadata_store.save()
        
        return vector_id
    
    def vectorize_persona_chunks(self, persona_id: str, persona_data: Dict[str, Any]) -> List[int]:
        """Persona profile을 여러 chunk로 vectorization."""
        if self.faiss_manager.index is None:
            self.faiss_manager.create_index()
        
        chunks = []
        chunk_labels = []
        
        if persona_data.get('traits'):
            traits_text = f"Personality traits: {', '.join(persona_data['traits'])}"
            chunks.append(traits_text)
            chunk_labels.append('traits')
        
        if persona_data.get('habits'):
            habits_text = f"Behavioral habits: {', '.join(persona_data['habits'])}"
            chunks.append(habits_text)
            chunk_labels.append('habits')
        
        if persona_data.get('goals'):
            goals_text = f"Long-term goals: {', '.join(persona_data['goals'])}"
            chunks.append(goals_text)
            chunk_labels.append('goals')
        
        if persona_data.get('background'):
            chunks.append(f"Background: {persona_data['background']}")
            chunk_labels.append('background')
        
        if persona_data.get('speech_style'):
            chunks.append(f"Speech style: {persona_data['speech_style']}")
            chunk_labels.append('speech_style')
        
        if persona_data.get('constraints'):
            constraints_text = f"Constraints: {json.dumps(persona_data['constraints'])}"
            chunks.append(constraints_text)
            chunk_labels.append('constraints')
        
        if not chunks:
            return []
        
        embeddings = embedding_service.embed(chunks)
        vector_ids = self.faiss_manager.add_vectors(embeddings)
        
        for i, (vector_id, chunk, label) in enumerate(zip(vector_ids, chunks, chunk_labels)):
            metadata = {
                'source_type': 'persona',
                'source_id': persona_id,
                'npc_id': None,
                'importance': 1.0,
                'created_at': persona_data.get('created_at', ''),
                'summary': chunk[:200],
                'chunk_type': label
            }
            self.metadata_store.add(metadata)
        
        self.faiss_manager.save_index()
        self.metadata_store.save()
        
        return vector_ids
    
    def vectorize_world_chunks(self, world_id: str, world_data: Dict[str, Any]) -> List[int]:
        """World knowledge를 여러 chunk로 vectorization."""
        if self.faiss_manager.index is None:
            self.faiss_manager.create_index()
        
        chunks = []
        chunk_labels = []
        
        if world_data.get('rules', {}).get('laws'):
            for law in world_data['rules']['laws']:
                chunks.append(f"Law: {law}")
                chunk_labels.append('law')
        
        if world_data.get('rules', {}).get('factions'):
            for faction_name, faction_desc in world_data['rules']['factions'].items():
                chunks.append(f"Faction {faction_name}: {faction_desc}")
                chunk_labels.append('faction')
        
        if world_data.get('rules', {}).get('social_norms'):
            for norm in world_data['rules']['social_norms']:
                chunks.append(f"Social norm: {norm}")
                chunk_labels.append('social_norm')
        
        if world_data.get('locations'):
            for loc_name, loc_info in world_data['locations'].items():
                loc_text = f"Location {loc_name}: {json.dumps(loc_info)}"
                chunks.append(loc_text)
                chunk_labels.append('location')
        
        if world_data.get('global_constraints'):
            constraints_text = f"Global constraints: {json.dumps(world_data['global_constraints'])}"
            chunks.append(constraints_text)
            chunk_labels.append('global_constraints')
        
        if not chunks:
            return []
        
        embeddings = embedding_service.embed(chunks)
        vector_ids = self.faiss_manager.add_vectors(embeddings)
        
        for i, (vector_id, chunk, label) in enumerate(zip(vector_ids, chunks, chunk_labels)):
            metadata = {
                'source_type': 'world',
                'source_id': world_id,
                'npc_id': None,
                'importance': 1.0,
                'created_at': world_data.get('created_at', ''),
                'summary': chunk[:200],
                'chunk_type': label
            }
            self.metadata_store.add(metadata)
        
        self.faiss_manager.save_index()
        self.metadata_store.save()
        
        return vector_ids
    
    def vectorize_persona_fact(
        self, 
        fact_id: str, 
        persona_id: str, 
        npc_id: Optional[str],
        dimension: str,
        content: str,
        source: str = "PeaCoK"
    ) -> int:
        """
        PersonaFact를 벡터로 인덱싱.
        
        Args:
            fact_id: Fact ID
            persona_id: Persona ID
            npc_id: NPC ID (optional)
            dimension: PeaCoK dimension (characteristic, routine_habit, etc.)
            content: Fact content
            source: Source of the fact (PeaCoK, Reflection, etc.)
        
        Returns:
            vector_id
        """
        if self.faiss_manager.index is None:
            self.faiss_manager.create_index()
        
        # 임베딩 텍스트: dimension 정보 포함
        embedding_text = f"[{dimension}] persona fact: {content}"
        
        embedding = embedding_service.embed_single(embedding_text)
        vector_ids = self.faiss_manager.add_vectors(embedding)
        vector_id = vector_ids[0]
        
        metadata = {
            'source_type': 'persona_fact',
            'source_id': fact_id,
            'persona_id': persona_id,
            'npc_id': npc_id,
            'dimension': dimension,
            'content': content,
            'source': source,
            'importance': 1.0,  # PersonaFact는 항상 중요
            'summary': content[:200]
        }
        self.metadata_store.add(metadata)
        
        self.faiss_manager.save_index()
        self.metadata_store.save()
        
        return vector_id
    
    def vectorize_persona_facts_bulk(
        self,
        facts: List[Dict[str, Any]]
    ) -> List[int]:
        """
        여러 PersonaFacts를 한 번에 벡터화.
        
        Args:
            facts: PersonaFact 딕셔너리 리스트
                각 dict는 fact_id, persona_id, npc_id, dimension, content, source 포함
        
        Returns:
            vector_id 리스트
        """
        if self.faiss_manager.index is None:
            self.faiss_manager.create_index()
        
        if not facts:
            return []
        
        # 임베딩 텍스트 생성
        embedding_texts = []
        for fact in facts:
            dimension = fact.get('dimension', 'characteristic')
            content = fact.get('content', '')
            embedding_text = f"[{dimension}] persona fact: {content}"
            embedding_texts.append(embedding_text)
        
        # 배치 임베딩
        embeddings = embedding_service.embed(embedding_texts)
        vector_ids = self.faiss_manager.add_vectors(embeddings)
        
        # 메타데이터 추가
        for i, (fact, vector_id) in enumerate(zip(facts, vector_ids)):
            metadata = {
                'source_type': 'persona_fact',
                'source_id': fact.get('fact_id', ''),
                'persona_id': fact.get('persona_id', ''),
                'npc_id': fact.get('npc_id'),
                'dimension': fact.get('dimension', 'characteristic'),
                'content': fact.get('content', ''),
                'source': fact.get('source', 'PeaCoK'),
                'importance': 1.0,
                'summary': fact.get('content', '')[:200]
            }
            self.metadata_store.add(metadata)
        
        self.faiss_manager.save_index()
        self.metadata_store.save()
        
        return vector_ids
    
    def reindex(self) -> None:
        """재인덱싱을 위해 초기화."""
        self.faiss_manager.create_index()
        self.metadata_store.clear()
    
    def get_vector_count(self) -> int:
        """Index의 vector 개수 조회."""
        return self.faiss_manager.get_vector_count()
    
    def search(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """유사한 vector 검색."""
        if self.faiss_manager.index is None:
            return []
        
        query_embedding = embedding_service.embed_single(query_text)
        distances, indices = self.faiss_manager.search(query_embedding, top_k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:
                continue
            
            metadata = self.metadata_store.get(int(idx))
            if metadata:
                result = metadata.copy()
                result['similarity_score'] = float(distance)
                results.append(result)
        
        return results
