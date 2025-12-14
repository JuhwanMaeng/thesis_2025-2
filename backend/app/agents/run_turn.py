"""NPC 턴 오케스트레이션 - 전체 인지 루프."""
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)
from app.agents.query_builder import QueryBuilder
from app.agents.reflection import ReflectionService, ReflectionTrigger
from app.memory.vector.vectorizer import Vectorizer
from app.agents.importance import ImportanceScorer
from app.agents.tools.dispatcher import ToolDispatcher
from app.agents.tools.schemas import Action
from app.services.llm_service import llm_service
from app.memory.vector.retriever import VectorRetriever
from app.memory.mongo.repository.npc_repo import NPCRepository
from app.memory.mongo.repository.persona_repo import PersonaRepository, PersonaFactRepository
from app.memory.mongo.repository.world_repo import WorldRepository
from app.memory.mongo.repository.memory_repo import MemoryRepository
from app.memory.mongo.repository.trace_repo import TraceRepository
from app.schemas.persona import PersonaFactDimension
from app.schemas.memory import MemoryCreate
from app.schemas.trace import TraceCreate


class TurnOrchestrator:
    """NPC 턴 오케스트레이터."""
    
    @staticmethod
    def _load_system_prompt() -> str:
        import os
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "system.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _load_planning_prompt() -> str:
        import os
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "planning.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Dimension당 최대 fact 개수 (프롬프트 길이 제한)
    MAX_FACTS_PER_DIMENSION = 3
    
    @staticmethod
    def _build_persona_fact_context(
        persona_id: str, 
        npc_id: Optional[str] = None, 
        max_facts_per_dimension: int = None
    ) -> str:
        """
        PersonaFact를 dimension별로 그룹화하여 프롬프트 컨텍스트 생성.
        
        Static facts를 우선 표시하고, Dynamic facts는 "(learned)" 표시와 함께 표시합니다.
        
        Args:
            persona_id: Persona ID
            npc_id: NPC ID (None이면 persona의 모든 facts, 지정하면 해당 NPC의 facts만)
            max_facts_per_dimension: Dimension당 최대 fact 개수 (None이면 기본값 사용)
        
        Returns:
            구조화된 PersonaFact 컨텍스트 문자열 (facts가 없으면 빈 문자열)
        """
        if max_facts_per_dimension is None:
            max_facts_per_dimension = TurnOrchestrator.MAX_FACTS_PER_DIMENSION
        # PersonaFacts 조회
        if npc_id:
            facts = PersonaFactRepository.get_facts_by_npc(npc_id)
        else:
            facts = PersonaFactRepository.get_facts_by_persona(persona_id)
        
        if not facts:
            return ""
        
        # Static과 Dynamic 분리
        static_facts = [f for f in facts if f.is_static]
        dynamic_facts = [f for f in facts if not f.is_static]
        
        # Dimension별로 그룹화
        dimension_groups = {
            PersonaFactDimension.CHARACTERISTIC: {"static": [], "dynamic": []},
            PersonaFactDimension.ROUTINE_HABIT: {"static": [], "dynamic": []},
            PersonaFactDimension.GOAL_PLAN: {"static": [], "dynamic": []},
            PersonaFactDimension.EXPERIENCE: {"static": [], "dynamic": []},
            PersonaFactDimension.RELATIONSHIP: {"static": [], "dynamic": []},
        }
        
        for fact in static_facts:
            if fact.dimension in dimension_groups:
                dimension_groups[fact.dimension]["static"].append(fact)
        
        for fact in dynamic_facts:
            if fact.dimension in dimension_groups:
                dimension_groups[fact.dimension]["dynamic"].append(fact)
        
        # 프롬프트 구성
        parts = []
        dimension_labels = {
            PersonaFactDimension.CHARACTERISTIC: "Character Traits",
            PersonaFactDimension.ROUTINE_HABIT: "Routines & Habits",
            PersonaFactDimension.GOAL_PLAN: "Goals & Plans",
            PersonaFactDimension.EXPERIENCE: "Experiences",
            PersonaFactDimension.RELATIONSHIP: "Relationships",
        }
        
        for dimension, label in dimension_labels.items():
            static_list = dimension_groups[dimension]["static"][:max_facts_per_dimension]
            dynamic_list = dimension_groups[dimension]["dynamic"][:max_facts_per_dimension]
            
            if not static_list and not dynamic_list:
                continue
            
            parts.append(f"{label}:")
            
            # Static facts 먼저
            for fact in static_list:
                parts.append(f"  - {fact.content}")
            
            # Dynamic facts (Reflection에서 생성된 것들)
            for fact in dynamic_list:
                parts.append(f"  - {fact.content} (learned)")
        
        return "\n".join(parts) if parts else ""
    
    @staticmethod
    def _build_persona_context(persona: Dict[str, Any], persona_id: str = None, npc_id: str = None, max_facts_per_dimension: int = None) -> str:
        """
        Persona 컨텍스트 빌드 (기존 PersonaProfile + PersonaFacts).
        
        Args:
            persona: PersonaProfile 딕셔너리
            persona_id: Persona ID (PersonaFact 조회용)
            npc_id: NPC ID (PersonaFact 조회용, 선택사항)
            max_facts_per_dimension: Dimension당 최대 fact 개수
        """
        parts = []
        parts.append(f"Name: {persona.get('name', 'Unknown')}")
        
        if persona.get('traits'):
            parts.append(f"Traits: {', '.join(persona['traits'])}")
        
        if persona.get('habits'):
            parts.append(f"Habits: {', '.join(persona['habits'])}")
        
        if persona.get('goals'):
            parts.append(f"Goals: {', '.join(persona['goals'])}")
        
        if persona.get('background'):
            parts.append(f"Background: {persona['background']}")
        
        if persona.get('speech_style'):
            parts.append(f"Speech Style: {persona['speech_style']}")
        
        if persona.get('constraints'):
            constraints = persona['constraints']
            if constraints.get('taboos'):
                parts.append(f"Taboos: {', '.join(constraints['taboos'])}")
            if constraints.get('moral_rules'):
                parts.append(f"Moral Rules: {', '.join(constraints['moral_rules'])}")
        
        # PersonaFacts 추가 (dimension별 그룹화)
        if persona_id:
            persona_fact_context = TurnOrchestrator._build_persona_fact_context(persona_id, npc_id, max_facts_per_dimension)
            if persona_fact_context:
                parts.append("\nPersona Facts:")
                parts.append(persona_fact_context)
        
        return "\n".join(parts)
    
    @staticmethod
    def _build_world_context(world: Dict[str, Any]) -> str:
        parts = []
        parts.append(f"World: {world.get('title', 'Unknown')}")
        
        rules = world.get('rules', {})
        if rules.get('laws'):
            parts.append(f"Laws: {', '.join(rules['laws'])}")
        if rules.get('social_norms'):
            parts.append(f"Social Norms: {', '.join(rules['social_norms'])}")
        if rules.get('factions'):
            parts.append("Factions:")
            for name, desc in rules['factions'].items():
                parts.append(f"  - {name}: {desc}")
        
        return "\n".join(parts)
    
    @staticmethod
    def _build_memory_context(retrieved_memories: List[Dict[str, Any]]) -> str:
        if not retrieved_memories:
            return "No relevant memories."
        
        parts = ["Relevant Memories:"]
        for i, mem in enumerate(retrieved_memories[:5], 1):  # Top 5
            summary = mem.get('summary', mem.get('content', ''))[:150]
            source_type = mem.get('source_type', 'unknown')
            parts.append(f"{i}. [{source_type}] {summary}")
        
        return "\n".join(parts)
    
    @staticmethod
    def run_turn(npc_id: str, observation: Dict[str, Any], turn_id: Optional[str] = None) -> Dict[str, Any]:
        """NPC 턴 실행 - 전체 인지 루프."""
        if not turn_id:
            turn_id = f"turn_{uuid.uuid4().hex[:8]}"
        
        # NPC 및 관련 데이터 조회
        npc = NPCRepository.get_npc_by_id(npc_id)
        if npc is None:
            raise ValueError(f"NPC {npc_id} not found")
        
        persona = PersonaRepository.get_persona_by_id(npc.persona_id)
        if persona is None:
            raise ValueError(f"Persona {npc.persona_id} not found")
        
        world = WorldRepository.get_world_by_id(npc.world_id)
        if world is None:
            raise ValueError(f"World {npc.world_id} not found")
        
        # NPC config 가져오기 (기본값 사용) - observation 저장 전에 필요
        npc_config = npc.config if npc.config else None
        if npc_config:
            if isinstance(npc_config, dict):
                from app.schemas.npc import NPCConfig
                npc_config = NPCConfig(**npc_config)
            retrieval_top_k = npc_config.retrieval_top_k
            importance_threshold = npc_config.importance_threshold
            reflection_threshold = npc_config.reflection_threshold
            max_facts_per_dimension = npc_config.max_facts_per_dimension
        else:
            retrieval_top_k = 5
            importance_threshold = 0.7
            reflection_threshold = 0.7
            max_facts_per_dimension = 3
        
        # 최근 대화 히스토리 가져오기 (observation 저장 전에 가져와서 현재 observation 제외)
        recent_memories = MemoryRepository.get_recent_memories(npc_id, limit=10, memory_type="short_term")
        recent_conversation = []
        for mem in recent_memories:
            if mem.source == "observation":
                recent_conversation.append(mem.content)
        
        # observation 저장 (단기 메모리)
        observation_summary = QueryBuilder.build_observation_summary(observation)
        memory_data = MemoryCreate(
            npc_id=npc_id,
            content=observation_summary,
            source="observation",
            importance=0.3,
            tags=["observation"]
        )
        observation_memory = MemoryRepository.insert_memory(memory_data, importance_threshold=importance_threshold)
        
        # retrieval query 구성 (대화 히스토리 포함)
        npc_goal = npc.current_state.get("goal", "")
        retrieval_query = QueryBuilder.build_retrieval_query(
            observation, 
            npc_goal=npc_goal,
            recent_conversation=recent_conversation if recent_conversation else None
        )
        
        # 벡터 메모리 검색 (observation 전달하여 dimension 추론)
        retriever = VectorRetriever()
        retrieval_result = retriever.retrieve_for_npc(
            npc_id, 
            retrieval_query, 
            top_k_per_index=retrieval_top_k,
            observation=observation
        )
        retrieved_memories = retrieval_result['retrieved_sources']
        retrieved_memory_ids = [mem.get('source_id') for mem in retrieved_memories if mem.get('source_id')]
        
        # 예측 importance 계산
        predicted_importance = ImportanceScorer.predict_importance(observation_summary)
        
        # emotion_delta 계산
        previous_emotion = npc.current_state.get("emotion", "neutral")
        current_emotion = observation.get("details", {}).get("emotion", previous_emotion)
        
        emotion_map = {
            "calm": 0.0, "neutral": 0.0, "happy": 0.3, "excited": 0.5,
            "sad": -0.3, "angry": -0.5, "fearful": -0.4, "surprised": 0.2
        }
        prev_emotion_val = emotion_map.get(previous_emotion.lower(), 0.0)
        curr_emotion_val = emotion_map.get(current_emotion.lower(), 0.0)
        emotion_delta = curr_emotion_val - prev_emotion_val
        
        # relationship_changed, quest_state_changed 감지
        details = observation.get("details", {})
        relationship_changed = "relationship" in details or "relation" in str(details).lower()
        quest_state_changed = "quest" in str(details).lower() or observation.get("event_type") == "quest_completed"
        
        # reflection trigger 결정 (NPC config의 reflection_threshold 사용)
        should_reflect = ReflectionTrigger.should_reflect(
            importance=predicted_importance,
            relationship_changed=relationship_changed,
            quest_state_changed=quest_state_changed,
            emotion_delta=emotion_delta,
            explicit_request=False,
            reflection_threshold=reflection_threshold
        )
        
        # reflection 실행
        reflection_summary = None
        reflection_used = False
        if should_reflect:
            persona_dict = persona.model_dump() if hasattr(persona, 'model_dump') else {
                'traits': persona.traits,
                'habits': persona.habits,
                'goals': persona.goals,
                'background': persona.background,
                'speech_style': persona.speech_style,
                'constraints': persona.constraints
            }
            reflection = ReflectionService.reflect(
                observation_summary,
                retrieved_memories,
                persona_dict
            )
            reflection_summary = f"Insights: {reflection['insights']}"
            reflection_used = True
            
            # Store reflection as long-term memory
            reflection_memory = MemoryCreate(
                npc_id=npc_id,
                content=reflection['insights'],
                source="reflection",
                importance=reflection['importance_score'],
                tags=["reflection"]
            )
            MemoryRepository.insert_memory(reflection_memory, importance_threshold=importance_threshold)
            
            # Update PersonaFacts from reflection
            persona_fact_updates = reflection.get('persona_fact_updates', [])
            if persona_fact_updates:
                created_fact_ids = ReflectionService.update_persona_facts(
                    npc_id=npc_id,
                    persona_id=npc.persona_id,
                    persona_fact_updates=persona_fact_updates
                )
                
                # 새로 생성된 PersonaFacts를 FAISS에 인덱싱
                if created_fact_ids:
                    persona_vectorizer = Vectorizer('persona')
                    for fact_id in created_fact_ids:
                        from app.memory.mongo.repository.persona_repo import PersonaFactRepository
                        fact = PersonaFactRepository.get_fact_by_id(fact_id)
                        if fact:
                            try:
                                persona_vectorizer.vectorize_persona_fact(
                                    fact_id=fact.fact_id,
                                    persona_id=fact.persona_id,
                                    npc_id=fact.npc_id,
                                    dimension=fact.dimension.value,
                                    content=fact.content,
                                    source=fact.source
                                )
                            except Exception as e:
                                logger.warning(f"Failed to index PersonaFact {fact_id}: {e}")
        
        # planning prompt 구성
        system_prompt = TurnOrchestrator._load_system_prompt()
        planning_prompt = TurnOrchestrator._load_planning_prompt()
        
        persona_context = TurnOrchestrator._build_persona_context(
            persona.model_dump() if hasattr(persona, 'model_dump') else {
                'name': persona.name,
                'traits': persona.traits,
                'habits': persona.habits,
                'goals': persona.goals,
                'background': persona.background,
                'speech_style': persona.speech_style,
                'constraints': persona.constraints
            },
            persona_id=npc.persona_id,
            npc_id=npc_id,
            max_facts_per_dimension=max_facts_per_dimension
        )
        
        world_context = TurnOrchestrator._build_world_context(
            world.model_dump() if hasattr(world, 'model_dump') else {
                'title': world.title,
                'rules': world.rules
            }
        )
        
        memory_context = TurnOrchestrator._build_memory_context(retrieved_memories)
        
        # 최근 대화 히스토리를 컨텍스트에 추가
        conversation_context = ""
        if recent_conversation and len(recent_conversation) > 0:
            conversation_items = recent_conversation[:5]  # 최근 5개만
            conversation_context = "\n".join([f"- {item}" for item in conversation_items])
            conversation_context = f"RECENT CONVERSATION:\n{conversation_context}\n"
        
        full_context = f"""PERSONA:
{persona_context}

WORLD:
{world_context}

{memory_context}

{conversation_context}CURRENT OBSERVATION:
{observation_summary}

{f'REFLECTION: {reflection_summary}' if reflection_summary else ''}
"""
        
        planning_prompt_full = f"{planning_prompt}\n\n{full_context}"
        
        # LLM 호출 (tool 선택)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": planning_prompt_full}
        ]
        
        llm_result = llm_service.call_with_tools(messages, use_tools=True)
        
        # tool call 검증 및 파싱
        if not llm_result['tool_calls']:
            action = Action(
                action_type="wait",
                arguments={"reason": "No tool call from LLM"},
                reason="LLM did not provide a tool call, defaulting to wait"
            )
        else:
            tool_call = llm_result['tool_calls'][0]
            parsed = llm_service.parse_tool_call(tool_call)
            
            if parsed:
                action = Action(
                    action_type=parsed['action_type'],
                    arguments=parsed['arguments'],
                    reason=llm_result['raw_output'] or "No reason provided"
                )
            else:
                action = Action(
                    action_type="wait",
                    arguments={"reason": "Invalid tool call"},
                    reason="LLM provided invalid tool call, defaulting to wait"
                )
        
        # tool 실행
        context = {
            "npc_id": npc_id,
            "current_location": npc.current_state.get("location", "unknown"),
            "world_id": npc.world_id,
            "persona_id": npc.persona_id
        }
        
        action_result = ToolDispatcher.execute_action(action, context)
        
        # action_result_dict 생성
        if hasattr(action_result, 'model_dump'):
            action_result_dict = action_result.model_dump()
        else:
            action_result_dict = {
                'success': action_result.success,
                'action_type': action_result.action_type,
                'effect': action_result.effect or {},
                'error': action_result.error or ''
            }
        
        # 실패 시 로깅 및 에러 정보 확실히 기록
        if not action_result_dict.get('success', False):
            error_msg = action_result_dict.get('error', '')
            if not error_msg:
                error_msg = f"Tool {action.action_type} execution failed without error message"
                action_result_dict['error'] = error_msg
            
            logger.error(
                f"Tool execution FAILED - "
                f"npc_id={npc_id}, turn_id={turn_id}, "
                f"action={action.action_type}, "
                f"arguments={action.arguments}, "
                f"error={error_msg}"
            )
        
        # importance 점수 계산 (정확한 값)
        importance_score, importance_justification = ImportanceScorer.score_importance(
            observation_summary,
            action_result_dict,
            reflection_summary
        )
        
        # inference trace 기록
        trace_data = TraceCreate(
            npc_id=npc_id,
            turn_id=turn_id,
            observation=observation_summary,
            retrieved_memories=retrieved_memory_ids,
            persona_used=npc.persona_id,
            world_used=npc.world_id,
            llm_prompt_snapshot=planning_prompt_full,
            llm_output_raw=llm_result['raw_output'],
            chosen_action=action.action_type,
            tool_arguments=action.arguments,
            tool_execution_result=action_result_dict,
            retrieval_query_text=retrieval_query,
            retrieval_indices_searched=retrieval_result['indices_searched'],
            retrieval_vector_ids=[int(vid) for vid in retrieval_result['retrieved_vector_ids'] if vid is not None],
            retrieval_similarity_scores=retrieval_result['similarity_scores']
        )
        
        trace = TraceRepository.insert_trace(trace_data)
        
        return {
            "action": action.model_dump() if hasattr(action, 'model_dump') else {
                'action_type': action.action_type,
                'arguments': action.arguments,
                'reason': action.reason
            },
            "result": action_result_dict,
            "reason": action.reason,
            "trace_id": trace.trace_id,
            "turn_id": turn_id,
            "importance_score": importance_score,
            "importance_justification": importance_justification,
            "reflection_used": reflection_used
        }
