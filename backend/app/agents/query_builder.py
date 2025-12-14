"""Query builder - observation을 retrieval query로 변환."""
from typing import Dict, Any


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
        
        parts = []
        
        if actor:
            parts.append(f"{actor}")
        
        parts.append(action)
        
        if target:
            parts.append(f"to/with {target}")
        
        if location:
            parts.append(f"at {location}")
        
        if details:
            detail_strs = []
            for key, value in details.items():
                if isinstance(value, (str, int, float)):
                    detail_strs.append(f"{key}: {value}")
            if detail_strs:
                parts.append(f"({', '.join(detail_strs)})")
        
        summary = " ".join(parts)
        return summary
    
    @staticmethod
    def build_retrieval_query(observation: Dict[str, Any], npc_goal: str = None) -> str:
        """Vector retrieval용 query 텍스트 생성."""
        observation_summary = QueryBuilder.build_observation_summary(observation)
        if npc_goal:
            query = f"{observation_summary}. Current goal: {npc_goal}"
        else:
            query = observation_summary
        
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
