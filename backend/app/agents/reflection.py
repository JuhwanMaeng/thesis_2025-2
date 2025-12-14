"""Reflection 로직 - 선택적 reflection trigger."""
import json
import logging
from typing import Dict, Any, Optional, List
from app.services.llm_service import llm_service
from app.core.config import settings
from app.memory.mongo.repository.persona_repo import PersonaFactRepository
from app.schemas.persona import PersonaFactCreate, PersonaFactDimension

logger = logging.getLogger(__name__)


class ReflectionTrigger:
    
    # Thresholds
    IMPORTANCE_THRESHOLD = 0.7
    EMOTION_DELTA_THRESHOLD = 0.3
    
    @staticmethod
    def should_reflect(
        importance: float,
        relationship_changed: bool = False,
        quest_state_changed: bool = False,
        emotion_delta: float = 0.0,
        explicit_request: bool = False
    ) -> bool:
        """reflection trigger 여부 결정."""
        if explicit_request:
            return True
        
        if importance >= ReflectionTrigger.IMPORTANCE_THRESHOLD:
            return True
        
        if relationship_changed:
            return True
        
        if quest_state_changed:
            return True
        
        if abs(emotion_delta) >= ReflectionTrigger.EMOTION_DELTA_THRESHOLD:
            return True
        
        return False


class ReflectionService:
    """Reflection 생성 서비스."""
    
    @staticmethod
    def _load_reflection_prompt() -> str:
        import os
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "reflection.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def reflect(
        observation_summary: str,
        retrieved_memories: List[Dict[str, Any]],
        persona_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reflection 생성."""
        reflection_prompt = ReflectionService._load_reflection_prompt()
        memory_summaries = []
        for mem in retrieved_memories[:5]:
            summary = mem.get('summary', mem.get('content', ''))[:100]
            memory_summaries.append(f"- {summary}")
        
        context = f"""RECENT OBSERVATION:
{observation_summary}

RELEVANT MEMORIES:
{chr(10).join(memory_summaries) if memory_summaries else "None"}

PERSONA CONTEXT:
Traits: {', '.join(persona_context.get('traits', []))}
Goals: {', '.join(persona_context.get('goals', []))}
"""
        
        messages = [
            {"role": "system", "content": reflection_prompt},
            {"role": "user", "content": context}
        ]
        
        response = llm_service.call_simple(messages)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            reflection = json.loads(response)
            
            return {
                "insights": reflection.get("insights", ""),
                "updated_goals": reflection.get("updated_goals", []),
                "relationship_updates": reflection.get("relationship_updates", {}),
                "importance_score": float(reflection.get("importance_score", 0.5)),
                "persona_fact_updates": reflection.get("persona_fact_updates", [])
            }
        except (json.JSONDecodeError, ValueError, KeyError):
            return {
                "insights": response[:200] if response else "No insights extracted",
                "updated_goals": [],
                "relationship_updates": {},
                "importance_score": 0.5,
                "persona_fact_updates": []
            }
    
    # PersonaFact 생성 최소 importance threshold
    PERSONA_FACT_IMPORTANCE_THRESHOLD = 0.8
    
    @staticmethod
    def update_persona_facts(
        npc_id: str,
        persona_id: str,
        persona_fact_updates: List[Dict[str, Any]],
        importance_threshold: float = None
    ) -> List[str]:
        """
        Reflection 결과에서 PersonaFact를 생성.
        
        중요도가 threshold 이상인 facts만 생성하며, 기존 facts와 중복 체크를 수행합니다.
        
        Args:
            npc_id: NPC ID
            persona_id: Persona ID
            persona_fact_updates: Reflection에서 추출한 PersonaFact 업데이트 리스트
            importance_threshold: PersonaFact 생성 최소 importance (None이면 기본값 사용)
        
        Returns:
            생성된 fact_id 리스트
        """
        if importance_threshold is None:
            importance_threshold = ReflectionService.PERSONA_FACT_IMPORTANCE_THRESHOLD
        created_fact_ids = []
        
        if not persona_fact_updates:
            return created_fact_ids
        
        # 기존 PersonaFacts 조회 (충돌 체크용)
        existing_facts = PersonaFactRepository.get_facts_by_persona(persona_id)
        existing_contents = {fact.content.lower().strip() for fact in existing_facts}
        
        for fact_update in persona_fact_updates:
            # Importance 체크
            importance = fact_update.get("importance", 0.0)
            if importance < importance_threshold:
                continue
            
            # Dimension 검증
            dimension_str = fact_update.get("dimension", "").lower()
            try:
                dimension = PersonaFactDimension(dimension_str)
            except (ValueError, AttributeError):
                # 매핑 시도
                dimension_map = {
                    "characteristic": PersonaFactDimension.CHARACTERISTIC,
                    "routine_habit": PersonaFactDimension.ROUTINE_HABIT,
                    "routine": PersonaFactDimension.ROUTINE_HABIT,
                    "habit": PersonaFactDimension.ROUTINE_HABIT,
                    "goal_plan": PersonaFactDimension.GOAL_PLAN,
                    "goal": PersonaFactDimension.GOAL_PLAN,
                    "plan": PersonaFactDimension.GOAL_PLAN,
                    "experience": PersonaFactDimension.EXPERIENCE,
                    "relationship": PersonaFactDimension.RELATIONSHIP,
                }
                dimension = dimension_map.get(dimension_str)
                if dimension is None:
                    continue
            
            # Content 추출
            content = fact_update.get("content", "").strip()
            if not content:
                continue
            
            # 중복 체크 (대소문자 무시)
            content_lower = content.lower().strip()
            if content_lower in existing_contents:
                continue  # 이미 존재하는 fact는 건너뛰기
            
            # PersonaFact 생성
            try:
                fact_data = PersonaFactCreate(
                    persona_id=persona_id,
                    npc_id=npc_id,
                    dimension=dimension,
                    content=content,
                    source="Reflection",
                    is_static=False  # Reflection에서 생성된 facts는 동적
                )
                
                fact = PersonaFactRepository.create_fact(fact_data)
                created_fact_ids.append(fact.fact_id)
                existing_contents.add(content_lower)
                
            except Exception as e:
                logger.warning(f"Failed to create PersonaFact: {content[:50]}... - {e}")
                continue
        
        return created_fact_ids
