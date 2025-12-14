"""Vector memory retrieval 전략."""
from typing import List, Dict, Any, Optional, Set
from app.memory.vector.vectorizer import Vectorizer
from app.services.embedding_service import embedding_service
from app.schemas.persona import PersonaFactDimension


class VectorRetriever:
    """Vector index에서 관련 memory 검색."""
    
    # PersonaFact 기본 가중치 (EpisodicMemory보다 높게)
    PERSONA_FACT_BASE_WEIGHT = 1.2
    EPISODIC_MEMORY_BASE_WEIGHT = 1.0
    
    # Dimension 매칭 가중치 (관련 dimension에 추가 부스팅)
    DIMENSION_MATCH_BOOST = 0.3
    
    def __init__(self):
        """각 index type용 retriever 초기화."""
        self.episodic_vectorizer = Vectorizer('episodic')
        self.persona_vectorizer = Vectorizer('persona')
        self.world_vectorizer = Vectorizer('world')
    
    @staticmethod
    def _infer_relevant_dimensions(query_text: str, observation: Optional[Dict[str, Any]] = None) -> Set[str]:
        """
        쿼리 텍스트와 관찰에서 관련 dimension 추론.
        
        Args:
            query_text: 검색 쿼리 텍스트
            observation: 현재 관찰 (선택사항)
        
        Returns:
            관련 dimension 값들의 집합
        """
        query_lower = query_text.lower()
        relevant_dims = set()
        
        # Characteristic 키워드
        characteristic_keywords = ['brave', 'coward', 'wise', 'foolish', 'kind', 'cruel', 
                                   'patient', 'impatient', 'protective', 'selfish', 'honest', 'deceptive']
        if any(kw in query_lower for kw in characteristic_keywords):
            relevant_dims.add(PersonaFactDimension.CHARACTERISTIC.value)
        
        # Routine/Habit 키워드
        routine_keywords = ['always', 'usually', 'often', 'routine', 'habit', 'regularly', 
                           'consistently', 'typically', 'normally']
        if any(kw in query_lower for kw in routine_keywords):
            relevant_dims.add(PersonaFactDimension.ROUTINE_HABIT.value)
        
        # Goal/Plan 키워드
        goal_keywords = ['goal', 'want', 'plan', 'intend', 'aim', 'purpose', 'objective', 
                        'strive', 'seek', 'desire', 'wish']
        if any(kw in query_lower for kw in goal_keywords):
            relevant_dims.add(PersonaFactDimension.GOAL_PLAN.value)
        
        # Experience 키워드
        experience_keywords = ['remember', 'recall', 'learned', 'experienced', 'happened', 
                              'before', 'past', 'memory', 'recall']
        if any(kw in query_lower for kw in experience_keywords):
            relevant_dims.add(PersonaFactDimension.EXPERIENCE.value)
        
        # Relationship 키워드
        relationship_keywords = ['friend', 'enemy', 'ally', 'mentor', 'student', 'relationship', 
                                'trust', 'betray', 'help', 'support', 'oppose']
        if any(kw in query_lower for kw in relationship_keywords):
            relevant_dims.add(PersonaFactDimension.RELATIONSHIP.value)
        
        # 관찰에서 action_type 기반 추론
        if observation:
            action_type = observation.get('event_type', '').lower()
            details = observation.get('details', {})
            
            # 전투 관련 → characteristic
            if 'combat' in action_type or 'fight' in action_type or 'attack' in action_type:
                relevant_dims.add(PersonaFactDimension.CHARACTERISTIC.value)
            
            # 대화 관련 → relationship
            if 'talk' in action_type or 'dialogue' in action_type or 'conversation' in action_type:
                relevant_dims.add(PersonaFactDimension.RELATIONSHIP.value)
            
            # 퀘스트 관련 → goal_plan
            if 'quest' in action_type:
                relevant_dims.add(PersonaFactDimension.GOAL_PLAN.value)
        
        return relevant_dims
    
    @staticmethod
    def _boost_persona_facts(
        results: List[Dict[str, Any]],
        relevant_dimensions: Set[str],
        base_weight: float = PERSONA_FACT_BASE_WEIGHT,
        dimension_boost: float = DIMENSION_MATCH_BOOST
    ) -> List[Dict[str, Any]]:
        """
        PersonaFact 결과에 가중치 부스팅 적용.
        
        Args:
            results: 검색 결과 리스트
            relevant_dimensions: 관련 dimension 집합
            base_weight: PersonaFact 기본 가중치
            dimension_boost: Dimension 매칭 시 추가 부스팅
        
        Returns:
            가중치가 적용된 결과 리스트
        """
        boosted_results = []
        
        for result in results:
            result = result.copy()
            original_score = result.get('similarity_score', 0.0)
            
            # PersonaFact인 경우 부스팅
            if result.get('source_type') == 'persona_fact':
                boosted_score = original_score * base_weight
                
                # Dimension 매칭 확인
                fact_dimension = result.get('dimension')
                if fact_dimension and fact_dimension in relevant_dimensions:
                    boosted_score += dimension_boost
                
                result['similarity_score'] = boosted_score
                result['original_score'] = original_score
                result['boost_applied'] = True
            
            boosted_results.append(result)
        
        return boosted_results
    
    def retrieve(
        self,
        query_text: str,
        top_k_per_index: int = 5,
        indices: Optional[List[str]] = None,
        observation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Vector index에서 관련 memory 검색 (PersonaFact 부스팅 포함).
        
        Args:
            query_text: 검색 쿼리 텍스트
            top_k_per_index: 각 인덱스당 가져올 결과 수
            indices: 검색할 인덱스 리스트
            observation: 현재 관찰 (dimension 추론용)
        
        Returns:
            검색 결과 딕셔너리
        """
        if indices is None:
            indices = ['episodic', 'persona', 'world']
        
        # 관련 dimension 추론
        relevant_dimensions = self._infer_relevant_dimensions(query_text, observation)
        
        all_results = []
        vector_ids = []
        similarity_scores = []
        
        for index_name in indices:
            if index_name == 'episodic':
                results = self.episodic_vectorizer.search(query_text, top_k_per_index)
            elif index_name == 'persona':
                results = self.persona_vectorizer.search(query_text, top_k_per_index)
            elif index_name == 'world':
                results = self.world_vectorizer.search(query_text, top_k_per_index)
            else:
                continue
            
            for result in results:
                all_results.append(result)
                vector_ids.append(result.get('vector_id'))
                similarity_scores.append(result.get('similarity_score', 0.0))
        
        # PersonaFact 부스팅 적용
        all_results = self._boost_persona_facts(all_results, relevant_dimensions)
        
        # 가중치 적용된 점수로 재정렬
        sorted_results = sorted(
            zip(all_results, vector_ids, [r.get('similarity_score', 0.0) for r in all_results]),
            key=lambda x: x[2],
            reverse=True
        )
        
        all_results = [r[0] for r in sorted_results]
        vector_ids = [r[1] for r in sorted_results]
        similarity_scores = [r[2] for r in sorted_results]
        
        return {
            'query_text': query_text,
            'indices_searched': indices,
            'top_k': top_k_per_index,
            'retrieved_vector_ids': vector_ids,
            'retrieved_sources': all_results,
            'similarity_scores': similarity_scores,
            'relevant_dimensions': list(relevant_dimensions)
        }
    
    def retrieve_for_npc(
        self,
        npc_id: str,
        query_text: str,
        top_k_per_index: int = 5,
        observation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        특정 NPC의 memory 검색 (episodic memory는 npc_id로 필터링, PersonaFact 부스팅 포함).
        
        Args:
            npc_id: NPC ID
            query_text: 검색 쿼리 텍스트
            top_k_per_index: 각 인덱스당 가져올 결과 수
            observation: 현재 관찰 (dimension 추론용)
        
        Returns:
            검색 결과 딕셔너리
        """
        results = self.retrieve(
            query_text, 
            top_k_per_index, 
            ['episodic', 'persona', 'world'],
            observation=observation
        )
        
        filtered_results = []
        filtered_vector_ids = []
        filtered_scores = []
        
        for result, vector_id, score in zip(
            results['retrieved_sources'],
            results['retrieved_vector_ids'],
            results['similarity_scores']
        ):
            # PersonaFact는 npc_id가 일치하거나 None인 경우 포함
            if result.get('source_type') == 'persona_fact':
                fact_npc_id = result.get('npc_id')
                if fact_npc_id is None or fact_npc_id == npc_id:
                    filtered_results.append(result)
                    filtered_vector_ids.append(vector_id)
                    filtered_scores.append(score)
            # 기존 persona (PersonaProfile chunks)는 모두 포함
            elif result.get('source_type') == 'persona':
                filtered_results.append(result)
                filtered_vector_ids.append(vector_id)
                filtered_scores.append(score)
            # World knowledge는 모두 포함
            elif result.get('source_type') == 'world':
                filtered_results.append(result)
                filtered_vector_ids.append(vector_id)
                filtered_scores.append(score)
            # Episodic memory는 npc_id로 필터링
            elif result.get('source_type') == 'episodic' and result.get('npc_id') == npc_id:
                filtered_results.append(result)
                filtered_vector_ids.append(vector_id)
                filtered_scores.append(score)
        
        return {
            'query_text': query_text,
            'indices_searched': results['indices_searched'],
            'top_k': top_k_per_index,
            'retrieved_vector_ids': filtered_vector_ids,
            'retrieved_sources': filtered_results,
            'similarity_scores': filtered_scores,
            'relevant_dimensions': results.get('relevant_dimensions', [])
        }
