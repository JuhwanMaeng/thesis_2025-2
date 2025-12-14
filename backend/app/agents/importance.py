"""LLM을 통한 importance 점수 계산."""
import json
from typing import Dict, Any, Optional
from app.services.llm_service import llm_service


class ImportanceScorer:
    """이벤트 importance 점수 계산."""
    
    @staticmethod
    def _load_importance_prompt() -> str:
        import os
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "importance.txt"
        )
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def score_importance(
        observation_summary: str,
        action_result: Dict[str, Any],
        reflection_summary: Optional[str] = None
    ) -> tuple[float, str]:
        """이벤트 중요도 점수 계산."""
        importance_prompt = ImportanceScorer._load_importance_prompt()
        
        context = f"""OBSERVATION:
{observation_summary}

ACTION RESULT:
{json.dumps(action_result, indent=2)}
"""
        
        if reflection_summary:
            context += f"\nREFLECTION:\n{reflection_summary}\n"
        
        messages = [
            {"role": "system", "content": importance_prompt},
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
            
            result = json.loads(response)
            
            importance_score = float(result.get("importance_score", 0.5))
            justification = result.get("justification", "No justification provided")
            
            importance_score = max(0.0, min(1.0, importance_score))
            
            return importance_score, justification
        except (json.JSONDecodeError, ValueError, KeyError):
            return 0.5, "Failed to parse importance score"
    
    @staticmethod
    def predict_importance(observation_summary: str) -> float:
        """observation만으로 예측 importance 계산 (reflection trigger용)."""
        importance_prompt = ImportanceScorer._load_importance_prompt()
        
        context = f"""OBSERVATION:
{observation_summary}

ACTION RESULT:
(Not yet available - prediction only)
"""
        
        messages = [
            {"role": "system", "content": importance_prompt},
            {"role": "user", "content": context}
        ]
        
        try:
            response = llm_service.call_simple(messages)
            
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            importance_score = float(result.get("importance_score", 0.5))
            importance_score = max(0.0, min(1.0, importance_score))
            
            return importance_score
        except (json.JSONDecodeError, ValueError, KeyError):
            return 0.5
