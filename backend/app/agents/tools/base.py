"""Base tool 인터페이스."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """모든 tool의 기본 클래스."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool 이름 (action_type과 일치해야 함)."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """LLM용 tool 설명 (영어)."""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """Tool 파라미터 JSON Schema."""
        pass
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 실행."""
        pass
    
    def to_openai_format(self) -> Dict[str, Any]:
        """OpenAI function calling 형식으로 변환."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
