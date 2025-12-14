"""Query builder - observation을 retrieval query로 변환."""
from typing import Dict, Any, List, Optional


class QueryBuilder:
    """Observation에서 retrieval query 생성."""
    
    @staticmethod
    def build_observation_summary(observation: Dict[str, Any]) -> str:
        """Observation JSON을 자연어 요약으로 변환."""
        event_type = observation.get('event_type', 'unknown')
        actor = observation.get('actor', 'unknown')
        target = observation.get('target', None)
        action = observation.get('action', 'did something')
        location = observation.get('location', None)
        details = observation.get('details', {})
        
        # dialogue가 있으면 action 대신 dialogue 사용 (중복 방지)
        dialogue = details.get('dialogue', None) if details else None
        if dialogue:
            action_text = dialogue
            action_verb = "said"
        else:
            action_text = action
            # event_type에 따라 동사 선택
            if event_type == 'player_interaction':
                action_verb = "said"
            elif event_type == 'combat':
                action_verb = "attacked"
            elif event_type == 'movement':
                action_verb = "moved"
            elif event_type == 'quest':
                action_verb = "quest action"
            else:
                action_verb = "action"
        
        parts = []
        
        if actor:
            parts.append(f"{actor}")
        
        # 동사와 액션을 자연스럽게 연결
        if action_verb == "said":
            parts.append(f"{action_verb}: \"{action_text}\"")
        else:
            parts.append(f"{action_verb}: {action_text}")
        
        if target:
            parts.append(f"to/with {target}")
        
        if location and location != 'unknown':
            parts.append(f"at {location}")
        
        # dialogue를 제외한 다른 details만 추가
        if details:
            detail_strs = []
            for key, value in details.items():
                # dialogue는 이미 action_text로 사용했으므로 제외
                if key != 'dialogue' and isinstance(value, (str, int, float)):
                    detail_strs.append(f"{key}: {value}")
            if detail_strs:
                parts.append(f"({', '.join(detail_strs)})")
        
        summary = " ".join(parts)
        return summary
    
    @staticmethod
    def build_retrieval_query(
        observation: Dict[str, Any], 
        npc_goal: str = None,
        recent_conversation: Optional[List[str]] = None
    ) -> str:
        """Vector retrieval용 query 텍스트 생성."""
        observation_summary = QueryBuilder.build_observation_summary(observation)
        
        query_parts = []
        
        # 최근 대화 히스토리 포함
        if recent_conversation and len(recent_conversation) > 0:
            # 최근 5개만 사용 (너무 길어지지 않도록)
            recent_items = recent_conversation[:5]
            conversation_context = ". ".join(recent_items)
            query_parts.append(f"Recent conversation: {conversation_context}")
        
        # 현재 observation
        query_parts.append(observation_summary)
        
        # Current goal
        if npc_goal:
            query_parts.append(f"Current goal: {npc_goal}")
        
        query = ". ".join(query_parts)
        return query
    
    @staticmethod
    def build_full_context(
        observation: Dict[str, Any],
        npc_goal: str = None,
        emotion: str = None
    ) -> str:
        """Prompt용 전체 context 문자열 생성."""
        observation_summary = QueryBuilder.build_observation_summary(observation)
        
        context_parts = [f"Observation: {observation_summary}"]
        
        if npc_goal:
            context_parts.append(f"Current goal: {npc_goal}")
        
        if emotion:
            context_parts.append(f"Current emotion: {emotion}")
        
        return "\n".join(context_parts)
